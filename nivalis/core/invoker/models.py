from typing import Callable
from dataclasses import dataclass

@dataclass
class Command:
    name: str
    allowed: bool
    func: Callable