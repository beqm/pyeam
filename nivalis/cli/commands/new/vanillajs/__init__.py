import os
import shutil
import questionary
from typing import List
from pathlib import Path
from ...models import DependencyObj

TEMPLATE_DIR = os.path.join(Path(__file__).resolve().parents[3], "templates", "options", "vanillajs")

def create_vanillajs_app(path: str):
    from . import features, typecheck
    from nivalis.cli.commands.utils import prompt_select, prompt_checkbox
    
    _typecheck: DependencyObj = prompt_select(title="Choose your type check",
        choices=[questionary.Choice(title=option.title, value=option) for option in typecheck.TypecheckEnum.__dict__.values() if isinstance(option, DependencyObj)]) 
    
    _features: List[DependencyObj] = prompt_checkbox(title="Choose your desired features", choices=[
        questionary.Choice(title=option.title, value=option)
        for option in features.FeaturesEnum.__dict__.values()
        if isinstance(option, DependencyObj)
        ])
    
    src_path = Path(TEMPLATE_DIR) / "base"
    dst_path = Path(os.getcwd()) / path

    shutil.copytree(src_path, dst_path, dirs_exist_ok=True)

    typecheck.resolve(path, _typecheck, _features)
    features.resolve(path, _typecheck, _features)