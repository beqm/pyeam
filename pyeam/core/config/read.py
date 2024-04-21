import json
from pyeam.core.models import Config

class ConfigHandler:

    @staticmethod
    def _read() -> None:
        with open('src-pyeam\pyeam.conf.json', encoding="utf-8") as config:
            return Config(json.load(config))