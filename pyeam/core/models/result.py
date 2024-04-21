from dataclasses import dataclass
from typing import Any

@dataclass
class Result():
    success: bool
    data: Any = None