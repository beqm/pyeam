import json
from dataclasses import dataclass


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
        self.project_name = config['productName']
        self.version = config['version']
        self.identifier = config['identifier']
        self.icon = config['icon']

        self.dev_tools = config['devTools']
        self.context_menu = config['contextMenu']
        self.build = BuildConfig(before_dev_command=config['build']['beforeDevCommand'], dev_url=config['build']['devUrl'],
                                 dist_dir=config['build']['distDir'], before_build_command=config['build']['beforeBuildCommand'])
        self.window = WindowConfig(title=config['window']['title'],
                                          width=config['window']['width'],
                                          height=config['window']['height'],
                                          resizable=config['window']['resizable'],
                                          min_height=config['window']['minHeight'],
                                          min_width=config['window']['minWidth'])
        

    def read(path: str, encoding: str) -> None:
        with open(path, encoding=encoding) as config:
            return Config(json.load(config))

