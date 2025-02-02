from dataclasses import dataclass

class TemplateEnum:
    REACT = "REACT"
    SVELTE = "SVELTE"

@dataclass
class PackageManager:
    execute: str
    cli: str

class PackageManagerEnum:
    NPM = PackageManager(execute="npm run", cli="npm")
    PNPM = PackageManager(execute="pnpm", cli="npm")