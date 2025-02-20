import os
import sys
import json
import time
import click
import shutil
import subprocess
import questionary
from pathlib import Path
from nivalis import bundler
from nivalis.tools import log
from nivalis.tools import stdout
from nivalis.cli.commands import utils

ENTRY_FOLDER_NAME = "src-python"
BUILD_FOLDER_NAME = "releases"
ENTRY_POINT_PATH = os.path.join(ENTRY_FOLDER_NAME, "main.py")
CONFIG_PATH = os.path.join(ENTRY_FOLDER_NAME, "nivalis.conf.json")

logger = log.get(log.LIB_LOGGER)

@click.command()
@click.option('--debug', is_flag=True, help="Enable console terminal")
@click.option('--verbose', '-v', is_flag=True, help="Change lib logger level to DEBUG")
@click.option('--skip-installer', is_flag=True, help="Skip the building of installer")
def build(debug: str, verbose, skip_installer):
    """Builds a existing project.
    """

    if verbose:
        logger.setLevel(log.DEBUG)

    if not os.path.isdir("src-python"):
        logger.info("Could not find `src-python`, changing directory")
        os.chdir(Path(os.path.dirname(os.getcwd())).resolve())
        if not os.path.isdir("src-python"):
            logger.error("Could not find application.")
            stdout.error("Could not find application.", exit=True)

    if not os.path.isfile(ENTRY_POINT_PATH):
        logger.error("Could not find `main.py`")
        stdout.error("Could not find application.", exit=True)

    if not os.path.isfile(CONFIG_PATH):
        logger.error("Could not find `nivalis.conf.json`")
        stdout.error("Could not find application.", exit=True)

    is_installable = None
    if not skip_installer:
        is_installable = utils.prompt_select(title=f"Create installer?", choices=[questionary.Choice(title="Yes", value=True),
            questionary.Choice(title="No", value=False)])
    
    logger.info("Reading config file")
    with open(CONFIG_PATH, "r") as file:
        config = json.load(file)


    version = config["version"]
    product_name = config["productName"]
    start = time.perf_counter()


    build_frontend(config)
    
    logger.info(f"Compiling {product_name}")
    stdout.info(f"Compiling {product_name}")
    os.makedirs("releases", exist_ok=True)

    OUTPUT_DIR = os.path.join(BUILD_FOLDER_NAME, version)

    if os.path.exists(OUTPUT_DIR):
        _continue = utils.prompt_select(title=f"Directory `releases/{version}` not empty, continue?", choices=[questionary.Choice(title="Yes", value=True),
            questionary.Choice(title="No", value=False)])       

        if not _continue:
            stdout.info("Operation cancelled by user.", exit=True)

    compile_executable(config, debug)

    if is_installable:
        exe_path = os.path.join(OUTPUT_DIR, f"{product_name}.exe")
        bundler.windows.msi.compile_installer(exe_path, config)

    end = time.perf_counter()
    timelapse = end - start
    stdout.info(f"Done in: {timelapse:.2f}s")

    if verbose:
        logger.setLevel(log.NOTSET)



def compile_executable(config, debug):
    version = config["version"]
    product_name = config["productName"]
    dist_dir = config["build"]["distDir"]

    build_dir = resolve_dist_dir(dist_dir)

    MODE = "--mode=" + "onefile"
    PYTHON_PATH = sys.executable if utils.is_venv() else "python"
    OUTPUT_DIR = "--output-dir=" + os.path.join(BUILD_FOLDER_NAME, version)
    INCLUDE_DIST = "--include-data-dir=" + f"{build_dir}={dist_dir}/"
    INCLUDE_CONFIG_FILE = "--include-data-files=" + f"{CONFIG_PATH}=nivalis.conf.json"
    INCLUDE_LIB = "--include-data-files=" + f"{os.path.join(utils.get_package_path("nivalis"), "core", "dlls")}\\*=nivalis/core/dlls/"

    CONSOLE_MODE = "--windows-console-mode=" + ("force" if debug else "hide")
    # ICON = "--windows-icon-from-ico=" + config["icon"]
    OUTPUT_NAME = "--output-filename=" + product_name
    PRODUCT_NAME = "--product-name=" + product_name
    COMPANY_NAME = "--company-name=" + product_name
    FILE_VERSION = "--file-version=" + version
    PRODUCT_VERSION = "--product-version=" + version

    cmd = [
        PYTHON_PATH, "-m", "nuitka", MODE,
        INCLUDE_DIST, INCLUDE_LIB, INCLUDE_CONFIG_FILE,
        OUTPUT_DIR, PRODUCT_NAME, COMPANY_NAME, FILE_VERSION,
        PRODUCT_VERSION, OUTPUT_NAME, CONSOLE_MODE,
        # ICON,
        ENTRY_POINT_PATH,
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as err:
        stdout.error(f"Failed to compile project: {err}", exit=True)


def resolve_dist_dir(name: str):
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
        logger.info(f"Running {build_command} command")
        stdout.info(f"Running {build_command} command")
        subprocess.run(build_command, shell=True, check=True)
        stdout.info(f"Build complete")
    except subprocess.CalledProcessError as err:
        logger.error(f"Failed to build frontend: {err}")
        stdout.error(f"Failed to build: {err}", exit=True)
