import os
import sys
import shutil
import subprocess
from typing import List
from pyeam.tools import stdout
import json
from pyeam.cli.config import TemplateEnum, PackageManager
import questionary

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


def generate_build_field(manager: PackageManager, template: TemplateEnum):
    build = {
        "beforeBuildCommand": "",
        "beforeDevCommand": "",
        "devUrl": "",
        "distDir": "",
    }

    match template:
        case TemplateEnum.SVELTE:
            build["beforeBuildCommand"] = f"{manager.execute} build"
            build["beforeDevCommand"] = f"{manager.execute} dev"
            build["devUrl"] = "http://localhost:5173"
            build["distDir"] = "../dist"
        case TemplateEnum.REACT:
            build["beforeBuildCommand"] = f"{manager.execute} build"
            build["beforeDevCommand"] = f"{manager.execute} dev"
            build["devUrl"] = "http://localhost:3000"
            build["distDir"] = "../build"
    
    return build

def scaffold_python(manager: PackageManager, path: str, template: TemplateEnum):
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", "python")

    os.makedirs(os.path.join(path, "src-pyeam"))
    
    src_main = os.path.join(templates_dir, "main.py")
    dst_main = os.path.join(path, "src-pyeam", "main.py")
    shutil.copy2(src_main, dst_main)

    src_json = os.path.join(templates_dir, "pyeam.conf.json")
    dst_json = os.path.join(path, "src-pyeam", "pyeam.conf.json")
    shutil.copy2(src_json, dst_json)

    with open(dst_json, 'r') as file:
        config = json.load(file)

    build_field = generate_build_field(manager, template)
    config['build'] = build_field

    with open(dst_json, 'w') as file:
        json.dump(config, file, indent=4)


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
            file.write("pyeam==0.1.0")
        return True, None
    except Exception as err:
        return False, err
    

def create_svelte_app(path: str):
    command = f"npx sv create {path} --no-install"
    subprocess.run(command, shell=True, check=True)

def create_react_app(path: str):
    command = f"npx create-react-app {path} --skip-install"
    subprocess.run(command, shell=True, check=True)

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
