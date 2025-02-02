import json
from dataclasses import dataclass
from pyeam.core.config.exceptions import PyeamConfigError

@dataclass
class WindowConfig:
    title: str
    width: float
    height: float
    resizable: bool
    min_height: float
    min_width: float


@dataclass
class BuildConfig:
    before_dev_command: str
    before_build_command: str
    dev_url: str
    dist_dir: str


@dataclass
class Config:
    project_name: str
    version: str
    identifier: str
    icon: str
    context_menu: bool
    dev_tools: bool
    build: BuildConfig
    window: WindowConfig

    def __init__(self, config: dict):
        self.validate_config(config)

        self.project_name = config['productName']
        self.version = config['version']
        self.identifier = config['identifier']
        self.icon = config['icon']
        self.dev_tools = config['devTools']
        self.context_menu = config['contextMenu']
        
        self.build = BuildConfig(
            before_dev_command=config['build']['beforeDevCommand'],
            before_build_command=config['build']['beforeBuildCommand'],
            dev_url=config['build']['devUrl'],
            dist_dir=config['build']['distDir']
        )

        self.window = WindowConfig(
            title=config['window']['title'],
            width=config['window']['width'],
            height=config['window']['height'],
            resizable=config['window']['resizable'],
            min_height=config['window']['minHeight'],
            min_width=config['window']['minWidth']
        )


    @staticmethod
    def validate_config(config: dict):
        required_fields = {
            "productName": str,
            "version": str,
            "identifier": str,
            "icon": str,
            "devTools": bool,
            "contextMenu": bool,
            "build": dict,
            "window": dict,
        }

        build_fields = {
            "beforeDevCommand": str,
            "beforeBuildCommand": str,
            "devUrl": str,
            "distDir": str,
        }

        window_fields = {
            "title": str,
            "width": (int, float),
            "height": (int, float),
            "resizable": bool,
            "minHeight": (int, float),
            "minWidth": (int, float),
        }

        for key, expected_type in required_fields.items():
            if key not in config:
                raise PyeamConfigError(f"Missing required field: {key}")
            if not isinstance(config[key], expected_type):
                raise PyeamConfigError(f"Incorrect type for {key}: expected {expected_type}, got {type(config[key])}")
            if isinstance(config[key], str) and not config[key]:
                if key == "icon":
                    continue
                raise PyeamConfigError(f"Field '{key}' cannot be empty")

        for key, expected_type in build_fields.items():
            if key not in config["build"]:
                raise PyeamConfigError(f"Missing required field in 'build': {key}")
            if not isinstance(config["build"][key], expected_type):
                raise PyeamConfigError(f"Incorrect type for build.{key}: expected {expected_type}, got {type(config['build'][key])}")

        for key, expected_type in window_fields.items():
            if key not in config["window"]:
                raise PyeamConfigError(f"Missing required field in 'window': {key}")
            if not isinstance(config["window"][key], expected_type):
                raise PyeamConfigError(f"Incorrect type for window.{key}: expected {expected_type}, got {type(config['window'][key])}")

        if config["window"]["width"] <= 0:
            raise PyeamConfigError("Width must be greater than 0")
        if config["window"]["height"] <= 0:
            raise PyeamConfigError("Height must be greater than 0")
        
    @staticmethod
    def read(path: str, encoding: str = "utf-8"):

        try:
            with open(path, encoding=encoding) as config_file:
                config_data = json.load(config_file)
                return Config(config_data)
        except Exception as err:
            raise PyeamConfigError(f"Failed to load pyeam config file: {err}")
