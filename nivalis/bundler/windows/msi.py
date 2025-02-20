import os
import uuid
import shutil
import requests
import subprocess
from typing import Dict
from pathlib import Path
from nivalis.bundler import utils
from nivalis.tools import stdout, log
import xml.etree.ElementTree as xml_et

logger = log.get(log.LIB_LOGGER)
DEFAULT_WXS_PATH = os.path.join(os.path.dirname(__file__), "default.wxs")


def compile_installer(path: str, config: Dict):
    
    temp_path = Path(os.path.dirname(path)) / "temp"
    os.makedirs(temp_path, exist_ok=True)
    wix_path = get_wix_path(temp_path)

    wxs_path = None
    msi_obj = resolve_msi_bundler_obj(config)

    if msi_obj:
        wxs_path = msi_obj.get("path", None)

    temp_wxs = os.path.join(temp_path, "temp.wxs")
    if not wxs_path:
        logger.info("No custom wxs found, using default")
        logger.info("Copying wxs template to temp folder")
        shutil.copy2(DEFAULT_WXS_PATH, temp_wxs)
        wxs_path = temp_wxs
        resolve_default_wxs_file(temp_wxs, config, path)

    candle_exe = wix_path / "candle.exe"
    light_exe = wix_path / "light.exe"

    candle_cmd = [
        str(candle_exe),
        "-arch", utils.get_system_architecture(),
        "-out", os.path.join(temp_path, "output.wixobj"), 
        str(wxs_path)
    ]

    logger.info("Running candle.exe")
    candle_process = subprocess.run(candle_cmd, capture_output=True, text=True)
    if candle_process.returncode != 0:
        logger.error(candle_process.stdout)
        stdout.error(candle_process.stdout, exit=True)

    msi_dir = os.path.join(os.path.dirname(path), "bundles", "msi")
    os.makedirs(msi_dir, exist_ok=True)

    msi_name = f"{config['productName']}-{config["version"]}.msi"
    msi_output = os.path.join(msi_dir, msi_name)

    light_cmd = [
        str(light_exe),
        os.path.join(temp_path, "output.wixobj"),
        "-out", f'{msi_output}',
        "-ext", "WixUIExtension",
    ]

    logger.info("Running light.exe")
    light_process = subprocess.run(light_cmd, capture_output=True, text=True)
    if light_process.returncode != 0:
        logger.error(light_process.stdout)
        stdout.error(light_process.stdout, exit=True)

    stdout.info(f"msi installer created at: `{Path(msi_output).parent}`")
    shutil.rmtree(temp_path)

def resolve_default_wxs_file(path, config, exe_path):
    tree = xml_et.parse(path)
    root = tree.getroot()

    exe_path = str(Path(exe_path).resolve())

    logger.info("Updating values in temp.wxs")

    product_name = config["productName"]
    version = config["version"]
    manufacturer = "nivalis"
    # icon_path = config["iconPath"]
    identifier = config["identifier"]
    guid = str(uuid.uuid5(uuid.NAMESPACE_DNS, identifier))

    ns = {"wix": "http://schemas.microsoft.com/wix/2006/wi"}

    product_node = root.find(".//wix:Product", ns)
    product_node.set("Name", product_name)
    product_node.set("Version", version)
    product_node.set("Manufacturer", manufacturer)
    product_node.set("UpgradeCode", guid)

    root.find(".//wix:Property[@Id='WIXUI_EXITDIALOGOPTIONALCHECKBOXTEXT']", ns).set("Value", f"Run {product_name}")
    root.find(".//wix:Directory[@Id='INSTALLFOLDER']", ns).set("Name", product_name)

    component = root.find(".//wix:Directory[@Id='INSTALLFOLDER']", ns)
    
    component.find(".//wix:RegistryValue", ns).set("Key", f"Software\\{manufacturer}\\{product_name}")
    component.find(".//wix:File", ns).set("Source", exe_path)


    shortcut_component = root.find(".//wix:Component[@Id='DesktopShortcutComponent']", ns)
    shortcut_component.find(".//wix:Shortcut", ns).set("Name", product_name)
    shortcut_component.find(".//wix:Shortcut", ns).set("Target", f"[INSTALLFOLDER]{product_name}.exe")
    shortcut_component.find(".//wix:RegistryValue", ns).set("Key", f"Software\\{manufacturer}\\{product_name}")
    
    logger.info("Saving values in temp.wxs")
    tree.write(path, encoding="utf-8", xml_declaration=True)


def download_wix_toolset(temp_path: Path):
    wix_url = "https://github.com/wixtoolset/wix3/releases/download/wix3141rtm/wix314-binaries.zip"
    
    logger.info("Downloading wix toolset")
    response = requests.get(wix_url, stream=True)
    zip_path = temp_path / "wix.zip"
    
    with open(zip_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    

    wix_path = Path(temp_path) / ".wix"
    logger.info("Unpacking files")
    shutil.unpack_archive(zip_path, wix_path)
    return wix_path

def get_wix_path(temp_path: Path) -> Path:

    path = Path(os.environ.get("WIX", ""))

    logger.info("Searching for installed wix path")
    if path.exists() and (path / "candle.exe").exists() and (path / "light.exe").exists():
        logger.info("Wix path found")
        return path
    
    logger.info("Could not find wix")
    return download_wix_toolset(temp_path)


def resolve_msi_bundler_obj(config):
    bundler_obj = config.get("bundler", None)
    if bundler_obj:
        return  bundler_obj.get("msi", None)
    return bundler_obj
