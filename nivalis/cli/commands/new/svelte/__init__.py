import os
import json
import shutil
import questionary
from pathlib import Path
from .models import DependencyObj
from typing import Dict, Any, List

SVELTE_TEMPLATE_DIR = os.path.join(Path(__file__).resolve().parents[3], "templates", "options", "svelte")

def create_svelte_app(path: str):
    from . import features, typecheck
    from nivalis.cli.commands.utils import prompt_select, prompt_checkbox
    
    typecheck_obj = prompt_select(title="Choose your type check",
        choices=[questionary.Choice(title=tc.title, value=tc) for tc in typecheck.TypecheckEnum.__dict__.values() if isinstance(tc, DependencyObj)]) 
    
    features_list = prompt_checkbox(title="Choose your desired features", choices=[
        questionary.Choice(title=tc.title, value=tc)
        for tc in features.FeaturesEnum.__dict__.values()
        if isinstance(tc, DependencyObj)
        ])
    
    src_path = os.path.join(SVELTE_TEMPLATE_DIR, "base")
    dst_path = os.path.join(os.getcwd(), path)

    shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
    os.makedirs(os.path.join(dst_path, "src", "lib"), exist_ok=True)

    typecheck.resolve_typecheck(path, typecheck_obj)
    features.resolve_features(path, features_list, typecheck_obj)

    resolve_package_json(path, features_list, typecheck_obj)


def resolve_package_json(path: str, features_list: List[DependencyObj], typecheck_obj: DependencyObj):
    json_path = os.path.join(os.getcwd(), path, "package.json")

    with open(json_path, 'r') as file:
        package_json: Dict[str, Any] = json.load(file)

    package_json["name"] = path if path != "." else "My app"


    package_json["devDependencies"].update(typecheck_obj.packages)
    for feature in features_list:
        package_json["devDependencies"].update(feature.packages)

    with open(json_path, 'w') as file:
        json.dump(package_json, file, indent=2)
