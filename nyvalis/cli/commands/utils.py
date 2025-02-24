import os
import sys
import json
import shutil
import subprocess
import questionary
import importlib.util
from typing import List
from pathlib import Path
import importlib.metadata
from nyvalis.tools import stdout, log
from nyvalis.core import CONF_FILENAME, LIB_NAME
from nyvalis.cli.commands.models import PackageManager, TemplateObj

logger = log.get(log.LIB_NAME)

def prompt_text(title: str, default):
    value = questionary.text(title, default=default).ask()

    if value is None:
        logger.info(f"{title}: Cancelled by user.")
        stdout.info("Operation cancelled by user", exit=True)
    
    return value


def prompt_select(title: str, choices: List[questionary.Choice]):
    value = questionary.select(
        title,
        choices=choices
    ).ask()

    if value is None:
        logger.info(f"{title}: Cancelled by user.")
        stdout.info("Operation cancelled by user", exit=True)
    
    return value

def prompt_checkbox(title: str, choices: List[questionary.Choice]):
    value = questionary.checkbox(
        title,
        choices=choices
    ).ask()

    if value is None:
        logger.info(f"{title}: Cancelled by user.")
        stdout.info("Operation cancelled by user", exit=True)
    
    return value


def resolve_conf_file(manager: PackageManager, template: TemplateObj, path: str):
    dst_json = os.path.join(path, "src-python", CONF_FILENAME)
    
    with open(dst_json, 'r') as file:
        config = json.load(file)

    name = "My App"
    if path != ".":
        name = path

    config["productName"] = name
    config["version"] = "0.1.0"
    config["identifier"] = f"com.{name}.app"
    config["window"]["title"] = name

    config["build"] = template.build_field.to_dict()

    for key in config["build"]:
        config["build"][key] = config["build"][key].replace(r"{{ manager }}", f"{manager.execute}")
    
    with open(dst_json, 'w') as file:
        json.dump(config, file, indent=4)

    log.info("Writing configuration file")

def scaffold_python(manager: PackageManager, path: str, template: TemplateObj):
    PYTHON_TEMPLATE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "templates" / "python"

    log.info("Scaffolding python")
    src_path = Path(path).resolve() / "src-python"
    shutil.copytree(PYTHON_TEMPLATE_DIR, src_path, dirs_exist_ok=True)

    resolve_conf_file(manager, template, path)
    log.info("Python template done")


def is_cli_installed(name: str, arg="-v") -> bool:
    try:
        subprocess.run([name, arg], capture_output=True, text=True, check=True, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False


def create_git_repo(path: str):
    try:
        subprocess.run(['git', 'init'], cwd=path, check=True)
        log.info("Git repository initialized in output directory.")
        stdout.info("Git repository initialized in output directory.")
    except subprocess.CalledProcessError as err:
        log.error(f"Failed to initialize Git: {err}")
        stdout.error(f"Failed to initialize Git: {err}", exit=True)

def write_requirements(path: str):
    try:
        with open(f"{path}/requirements.txt", "w") as file:
            file.write(f"{LIB_NAME}=={importlib.metadata.version(LIB_NAME)}")
        log.info("Sucessfully created requirements.txt")
    except Exception as err:
        log.error(f"Failed to write requirements.txt: {err}")
        stdout.error(f"Failed to write requirements.txt: {err}", exit=True)
    

def setup_venv(path: str):
    stdout.info("Setting up venv...")
    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], cwd=path, check=True)
        log.info("Venv created")
        stdout.info("Venv created")
    except Exception as err:
        log.error(f"Failed to set up venv: {err}")
        stdout.error(f"Failed to set up venv: {err}")
    

def run_pip_install(path: str, venv: bool):
    stdout.info("Running pip install")
    try:
        if venv:
            pip_command = os.path.join(path, ".venv", "Scripts", "pip")
        else:
            pip_command = "pip"
        subprocess.run([pip_command, "install", "-r", "requirements.txt"], cwd=path, check=True)
        log.info("Pip dependencies installed successfully.")
        stdout.info("Pip dependencies installed successfully.")

    except Exception as err:
        log.error(f"Failed to install pip dependencies: {err}")
        stdout.error(f"Failed to install pip dependencies: {err}")

def run_npm_install(path: str, manager: PackageManager):
    stdout.info(f"Running {manager.cli} install")
    subprocess.run([manager.cli, "install"], cwd=path, check=True, shell=True)
    log.info("Node dependencies installed successfully.")
    stdout.info("Node dependencies installed successfully.")

def get_package_path(package_name):
    package_spec = importlib.util.find_spec(package_name)
    return os.path.dirname(package_spec.origin)

def is_venv():
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))