from pathlib import Path
from dataclasses import dataclass
from typing import Callable, Dict, Any


@dataclass
class BuildField:
    dev_url: str
    dist_dir: str
    dev_command: str
    build_command: str

    def to_dict(self):
        return {
            "devUrl": self.dev_url,
            "distDir": self.dist_dir,
            "beforeBuildCommand": self.build_command,
            "beforeDevCommand": self.dev_command,
        }


@dataclass
class TemplateObj:
    title: str
    value: str
    create: Callable
    build_field: BuildField


@dataclass
class FeaturePath:
    src: Path
    dst: Path


@dataclass
class DependencyObj:
    title: str
    value: str
    packages: Dict[str, str]
    extras: Dict[str, Any]
 

@dataclass
class PackageManager:
    execute: str
    cli: str

class PackageManagerEnum:
    NPM = PackageManager(execute="npm run", cli="npm")
    PNPM = PackageManager(execute="pnpm", cli="npm")
    