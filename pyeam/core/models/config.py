from dataclasses import dataclass

@dataclass
class WindowConfig:
    title: str
    width: float
    height: float
    resizable: bool

@dataclass
class BuildConfig:
    dev_command: str
    dev_url: str


@dataclass
class Config:
    project_name: str
    version: str
    build: BuildConfig
    window: WindowConfig


    def __init__(self, config: dict):
        self.project_name = config['projectName']
        self.version = config['version']
        self.build = BuildConfig(dev_command=config['build']['devCommand'], dev_url=config['build']['devUrl'])
        self.window = WindowConfig(title=config['window']['title'],
                                          width=config['window']['width'],
                                          height=config['window']['height'],
                                          resizable=config['window']['resizable'])


