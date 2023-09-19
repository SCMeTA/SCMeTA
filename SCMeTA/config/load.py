from configparser import ConfigParser
from pathlib import Path

import platform

from .default import DEFAULT_CONFIG

CONFIG_DIR = Path("~/.scmeta").expanduser()
CONFIG_PATH = CONFIG_DIR / "config.ini"
SYSTEM = platform.system()

def get_config():
    parser = ConfigParser()
    if not CONFIG_PATH.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            f.write(DEFAULT_CONFIG)
    parser.read(CONFIG_PATH)
    return parser


class Parameters:
    def __init__(self, parameters):
        self.parameters = parameters

    def __getattr__(self, item):
        value = self.parameters[item]
        if value.isdigit():
            value = int(value)
        elif value.replace(".", "", 1).isdigit():
            value = float(value)
        elif value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False
        elif value.lower() == "none":
            value = None
        return value

    def __getitem__(self, item):
        return self.__getattr__(item)


config = get_config()


PARAMETERS = Parameters(config["PARAMETERS"])
METABOLITE = Parameters(config["METABOLITE"])
