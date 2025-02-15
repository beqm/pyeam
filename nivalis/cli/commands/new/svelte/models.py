from typing import Callable, Dict
from dataclasses import dataclass


@dataclass
class DependencyObj:
    title: str
    value: str
    func: Callable
    packages: Dict[str, str]
