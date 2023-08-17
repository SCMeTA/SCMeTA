from configparser import ConfigParser
from pathlib import PureWindowsPath

import platform

SYSTEM = platform.system()

config_path = "config/config.ini"

if SYSTEM == "Windows":
    config_path = PureWindowsPath(config_path)

config = ConfigParser()
config.read(config_path)
PARAMETERS = config["PARAMETERS"]
METABOLITE = config["METABOLITE"]


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


PARAMETERS = Parameters(PARAMETERS)
METABOLITE = Parameters(METABOLITE)
