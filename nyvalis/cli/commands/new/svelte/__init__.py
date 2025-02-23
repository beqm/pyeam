import os
import shutil
import questionary
from typing import List
from pathlib import Path
from nyvalis.tools import log
from ...models import DependencyObj

logger = log.get(log.LIB_NAME)
TEMPLATE_DIR = os.path.join(Path(__file__).resolve().parents[3], "templates", "options", "svelte")

def create_svelte_app(path: str):
    from . import features, typecheck
    from nyvalis.cli.commands.utils import prompt_select, prompt_checkbox
    
    _typecheck: DependencyObj = prompt_select(title="Choose your type check",
        choices=[questionary.Choice(title=option.title, value=option) for option in typecheck.TypecheckEnum.__dict__.values() if isinstance(option, DependencyObj)]) 
    
    _features: List[DependencyObj] = prompt_checkbox(title="Choose your desired features", choices=[
        questionary.Choice(title=option.title, value=option)
        for option in features.FeaturesEnum.__dict__.values()
        if isinstance(option, DependencyObj)
        ])
    
    logger.info(f"typecheck: {_typecheck}")
    logger.info(f"features: {_features}")
    
    src_path = Path(TEMPLATE_DIR) / "base"
    dst_path = Path(os.getcwd()) / path

    logger.info(f"Scaffolding tempalte")
    shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
    logger.info(f"Template ready")

    typecheck.resolve(path, _typecheck, _features)
    features.resolve(path, _typecheck, _features)