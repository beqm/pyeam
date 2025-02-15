import os
import sys
import json
import shutil
import subprocess
import questionary
from typing import List
from nivalis.tools import stdout
from nivalis.cli.commands.models import PackageManager, TemplateEnum

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


def resolve_conf_file(manager: PackageManager, template: TemplateEnum, path: str):
    dst_json = os.path.join(path, "src-python", "nivalis.conf.json")
    
    with open(dst_json, 'r') as file:
        config = json.load(file)

    name = "My App"
    if path != ".":
        name = path

    config["productName"] = name
    config["window"]["title"] = name

    match template:
        case TemplateEnum.SVELTE.value:
            config["build"]["beforeBuildCommand"] = TemplateEnum.SVELTE.build_command.replace(r"{{ manager }}", f"{manager.execute}")
            config["build"]["beforeDevCommand"] = TemplateEnum.SVELTE.dev_command.replace(r"{{ manager }}", f"{manager.execute}")
            config["build"]["devUrl"] = TemplateEnum.SVELTE.dev_url
            config["build"]["distDir"] = TemplateEnum.SVELTE.dist_dir
        case TemplateEnum.REACT.value:
            config["build"]["beforeBuildCommand"] = TemplateEnum.REACT.build_command.replace(r"{{ manager }}", f"{manager.execute}")
            config["build"]["beforeDevCommand"] = TemplateEnum.REACT.dev_command.replace(r"{{ manager }}", f"{manager.execute}")
            config["build"]["devUrl"] = TemplateEnum.REACT.dev_url
            config["build"]["distDir"] = TemplateEnum.REACT.dist_dir
    
    with open(dst_json, 'w') as file:
        json.dump(config, file, indent=4)

def scaffold_python(manager: PackageManager, path: str, template: TemplateEnum):
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", "python")

    os.makedirs(os.path.join(path, "src-python"), exist_ok=True)
    
    src_main = os.path.join(templates_dir, "main.py")
    dst_main = os.path.join(path, "src-python", "main.py")
    shutil.copy2(src_main, dst_main)

    src_json = os.path.join(templates_dir, "nivalis.conf.json")
    dst_json = os.path.join(path, "src-python", "nivalis.conf.json")
    shutil.copy2(src_json, dst_json)

    resolve_conf_file(manager, template, path)


def is_npm_installed():
    try:
        subprocess.run(['npm', '-v'], capture_output=True, text=True, check=True, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False
    

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
