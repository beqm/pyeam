import os
import sys
import json
import shutil
import subprocess
import questionary
import importlib.util
from typing import List
from pathlib import Path
from nivalis.tools import stdout
from nivalis.cli.commands.models import PackageManager, TemplateObj


def prompt_text(title: str, default):
    value = questionary.text(title, default=default).ask()

    if value is None:
        stdout.info("Operation cancelled by user")
        sys.exit(0)
    
    return value


def prompt_select(title: str, choices: List[questionary.Choice]):
    value = questionary.select(
        title,
        choices=choices
    ).ask()

    if value is None:
        stdout.info("Operation cancelled by user")
        sys.exit(0)
    
    return value

def prompt_checkbox(title: str, choices: List[questionary.Choice]):
    value = questionary.checkbox(
        title,
        choices=choices
    ).ask()

    if value is None:
        stdout.info("Operation cancelled by user")
        sys.exit(0)
    
    return value


def resolve_conf_file(manager: PackageManager, template: TemplateObj, path: str):
    dst_json = os.path.join(path, "src-python", "nivalis.conf.json")
    
    with open(dst_json, 'r') as file:
        config = json.load(file)

    name = "My App"
    if path != ".":
        name = path

    config["productName"] = name
    config["window"]["title"] = name

    config["build"] = template.build_field.to_dict()

    for key in config["build"]:
        config["build"][key] = config["build"][key].replace(r"{{ manager }}", f"{manager.execute}")
    
    with open(dst_json, 'w') as file:
        json.dump(config, file, indent=4)

def scaffold_python(manager: PackageManager, path: str, template: TemplateObj):
    PYTHON_TEMPLATE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "templates" / "python"

    src_path = Path(path).resolve() / "src-python"
    shutil.copytree(PYTHON_TEMPLATE_DIR, src_path, dirs_exist_ok=True)

    resolve_conf_file(manager, template, path)

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
        stdout.info("Git repository initialized in output directory.")
    except subprocess.CalledProcessError as err:
        stdout.error(f"Failed to initialize Git: {err}", exit=True)

def write_requirements(path: str):
    try:
        with open(f"{path}/requirements.txt", "w") as file:
            file.write("nivalis==0.1.0")
    except Exception as err:
        stdout.error(f"Failed to write requirements.txt: {err}", exit=True)
    

def setup_venv(path: str):
    stdout.info("Setting up venv...")
    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], cwd=path, check=True)
    except Exception as err:
        stdout.error(f"Failed to set up venv: {err}")
    stdout.info("Venv created")

def run_pip_install(path: str, venv: bool):
    stdout.info("Running pip install")
    try:
        if venv:
            pip_command = os.path.join(path, ".venv", "Scripts", "pip")
        else:
            pip_command = "pip"
        subprocess.run([pip_command, "install", "-r", "requirements.txt"], cwd=path, check=True)
    except Exception as err:
        stdout.error(f"Failed to install pip dependencies: {err}")
    stdout.info("Pip dependencies installed successfully.")

def run_npm_install(path: str, manager: PackageManager):
    stdout.info(f"Running {manager.cli} install")
    subprocess.run([manager.cli, "install"], cwd=path, check=True, shell=True)
    stdout.info("Node dependencies installed successfully.")

def get_package_path(package_name):
    package_spec = importlib.util.find_spec(package_name)
    return os.path.dirname(package_spec.origin)

def is_venv():
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))