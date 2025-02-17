import os
import sys
import json
import click
import subprocess
import questionary
import importlib.util
import time
from nivalis.tools import stdout
from nivalis.cli.commands import utils

@click.command()
@click.option('--debug', is_flag=True, help="Enable console terminal")
def build(debug: str):
    entry_folder = "src-python"
    build_folder = "releases"
    entry_point = os.path.join(entry_folder, "main.py")
    config_path = os.path.join(entry_folder, "nivalis.conf.json")

    if not os.path.isdir("src-python"):
        stdout.error("Could not find application.", exit=True)

    if not os.path.isfile(entry_point):
        stdout.error("Could not find application.", exit=True)

    if not os.path.isfile(config_path):
        stdout.error("Could not find application.", exit=True)

    # is_installable = utils.prompt_select(title=f"Create installer?", choices=[questionary.Choice(title="Yes", value=True),
    #     questionary.Choice(title="No", value=False)])
    
    config = get_config(config_path)

    version = config["version"]
    product_name = config["productName"]

    config_dist_dir = config["build"]["distDir"]

    start = time.perf_counter()

    build_frontend(config)
    build_dir = get_dist_dir(config_dist_dir)

    stdout.info(f"Compiling {product_name}")
    os.makedirs("releases", exist_ok=True)

    OUTPUT_DIR = os.path.join(build_folder, version)

    if os.path.exists(OUTPUT_DIR):
        _continue = utils.prompt_select(title=f"Directory `releases/{version}` not empty, continue?", choices=[questionary.Choice(title="Yes", value=True),
            questionary.Choice(title="No", value=False)])       

        if not _continue:
            stdout.info("Operation cancelled by user.", exit=True)


    MODE = "--mode=" + "onefile"
    PYTHON_PATH = sys.executable if is_venv() else "python"
    OUTPUT_DIR = "--output-dir=" + os.path.join(build_folder, version)
    INCLUDE_DIST = "--include-data-dir=" + f"{build_dir}={config_dist_dir}/"
    INCLUDE_CONFIG_FILE = "--include-data-files=" + f"{os.path.join(entry_folder, "nivalis.conf.json")}=nivalis.conf.json"
    INCLUDE_LIB = "--include-data-files=" + f"{os.path.join(get_package_path("nivalis"), "core", "dlls")}\\*=nivalis/core/dlls/"

    CONSOLE_MODE = "--windows-console-mode=" + ("force" if debug else "hide")
    # ICON = "--windows-icon-from-ico=" + config["icon"]
    OUTPUT_NAME = "--output-filename=" + config["productName"]
    PRODUCT_NAME = "--product-name=" + config["productName"]
    COMPANY_NAME = "--company-name=" + config["productName"]
    FILE_VERSION = "--file-version=" + config["version"]
    PRODUCT_VERSION = "--product-version=" + config["version"]

    cmd = [
        PYTHON_PATH, "-m", "nuitka",
        MODE,
        INCLUDE_DIST,
        INCLUDE_LIB,
        INCLUDE_CONFIG_FILE,
        OUTPUT_DIR,
        PRODUCT_NAME,
        COMPANY_NAME,
        FILE_VERSION,
        PRODUCT_VERSION,
        OUTPUT_NAME,
        CONSOLE_MODE,
        # ICON,
        entry_point,
    ]

    try:
        subprocess.run(cmd, check=True)
        end = time.perf_counter()
        timelapse = end - start
        stdout.info(f"Compiled in: {timelapse:.2f}s")
    except subprocess.CalledProcessError as err:
        stdout.error(f"Failed to compile project: {err}", exit=True)

def get_package_path(package_name):
    package_spec = importlib.util.find_spec(package_name)
    return os.path.dirname(package_spec.origin)

def get_dist_dir(name: str):
    current_dir = os.getcwd()
    if os.path.isdir(os.path.join(current_dir, name)):
        return os.path.join(current_dir, name)

    parent_dir = os.path.dirname(current_dir)
    if os.path.isdir(os.path.join(parent_dir, name)):
        return os.path.join(parent_dir, name)

    stdout.error("Failed to find build directory", exit=True)

def build_frontend(config: dict):
    build_command = config["build"]["beforeBuildCommand"]

    try:
        stdout.info(f"Running {build_command} command")
        subprocess.run(build_command, shell=True, check=True)
        stdout.info(f"Build complete")
    except subprocess.CalledProcessError as e:
        stdout.error(f"Failed to build: {e}", exit=True)

def get_config(path: str):
    with open(path, "r") as file:
        return json.load(file)

def is_venv():
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))
