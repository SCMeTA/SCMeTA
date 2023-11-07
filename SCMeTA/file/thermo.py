import pandas as pd
import os

from pyRawTools import MSLoader

from .format import SCData
from SCMeTA.config import SYSTEM


def load_txt(path):
    raw = pd.read_table(path)
    raw = raw.drop(columns=["RetentionTime"])
    raw = raw.set_index("Scan")
    return raw


def load_raw(path):
    loader = MSLoader()
    if os.environ.get("CONTAINER"):
        temp_dir = "/ramdisk"
    else:
        temp_dir = None
    raw = loader.load(path, temp_dir=temp_dir)
    raw = raw.drop(columns=["RetentionTime"])
    return raw


def load_thermo_data(name, path) -> SCData:
    data = SCData(name)
    if SYSTEM == "Windows" and path.endswith(".txt"):
        data.raw = load_txt(path)
    elif SYSTEM == "Linux" or SYSTEM == "Darwin" and path.lower().endswith(".raw"):
        data.raw = load_raw(path)
    else:
        raise FileNotFoundError("File not supported")
    return data
