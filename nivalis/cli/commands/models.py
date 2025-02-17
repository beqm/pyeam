from typing import Callable
from dataclasses import dataclass


@dataclass
class TemplateObj:
    title: str
    value: str
    func: Callable
    dev_url: str
    dist_dir: str
    dev_command: str
    build_command: str

class TemplateEnum:
    from nivalis.cli.commands.new.svelte import create_svelte_app
    
    SVELTE = TemplateObj("Svelte", "SVELTE", create_svelte_app, 
                         dev_url="http://localhost:5173", dist_dir="dist", 
                         dev_command=r"{{ manager }} dev", build_command=r"{{ manager }} build")
    REACT = TemplateObj("React", "REACT", create_svelte_app, 
                        dev_url="http://localhost:3000", dist_dir="build", 
                        dev_command=r"{{ manager }} dev", build_command=r"{{ manager }} build")


@dataclass
class PackageManager:
    execute: str
    cli: str

class PackageManagerEnum:
    NPM = PackageManager(execute="npm run", cli="npm")
    PNPM = PackageManager(execute="pnpm", cli="npm")