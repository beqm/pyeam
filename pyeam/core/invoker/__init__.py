import sys
import json
import logging
from .models import Command
from pyeam.tools import stdout
from typing import Callable, Dict

class Invoker:
    commands: Dict[str, Command] = {}
    logger = logging.getLogger("pyeam")

    @classmethod
    def register(cls, name: str, func: Callable):
        if cls.commands.get(name):
            cls.logger.critical(f"Command with same name was found: `{name}`")
            stdout.error(f"Command with same name was found: `{name}`")
            sys.exit(1)
        
        cls.logger.info(f"Command `{name}` registered")
        cls.commands[name] = Command(name=func.__name__, allowed=False, func=func)

    @classmethod
    def process(cls, command: Command, params):
        try:
            result = command.func(**params)
            response = json.dumps({"data": str(result), "error": None})
            return response
        except Exception as err:
            cls.logger.error(err)
            response = json.dumps({"data": None, "error": str(err)})
            return response

def command(func):
    Invoker.commands[func.__name__] = Command(name=func.__name__, allowed=False, func=func)
    return func