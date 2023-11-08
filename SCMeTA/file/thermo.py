import pandas as pd
import os

from pyRawTools import MSLoader

from .format import SCData
from .plugin import RawFileReader

from SCMeTA.config import SYSTEM


def load_txt(path):
    raw = pd.read_table(path)
    raw = raw.drop(columns=["RetentionTime"])
    raw = raw.set_index("Scan")
    return raw


def load_darwin(path):
    loader = MSLoader()
    if os.environ.get("CONTAINER"):
        temp_dir = "/ramdisk"
    else:
        temp_dir = None
    raw = loader.load(path, temp_dir=temp_dir)
    raw = raw.drop(columns=["RetentionTime"])
    return raw


def load_dotnet(path):
    file = RawFileReader(path)
    raw = file.GetFullScanMassList()
    file.Close()
    return raw


IMPORT_FUNC = {
    "Darwin": load_darwin,
    "Windows": load_dotnet,
    "Linux": load_dotnet,
}


def load_thermo_data(name, path) -> SCData:
    data = SCData(name)
    if path.lower().endswith(".raw"):
        data.raw = IMPORT_FUNC[SYSTEM](path)
    elif path.lower().endswith(".txt"):
        data.raw = load_txt(path)
    else:
        raise FileNotFoundError("File not supported")
    return data
