import pandas as pd

from .format import SCData
from . import RawFileReader


def load_txt(path):
    raw = pd.read_table(path)
    raw = raw.drop(columns=["RetentionTime"])
    raw = raw.set_index("Scan")
    return raw


def load_thermo(path, include_ms2=False):
    reader = RawFileReader(file_path=path)
    data = reader.to_dataframe(include_ms2=include_ms2, filter_threshold=10)
    data.set_index("Scan", inplace=True)
    data = data.drop(columns=["RetentionTime"])

    return data


def load_thermo_data(name, path) -> SCData:
    data = SCData(name)
    if path.lower().endswith(".raw"):
        data.raw = load_thermo(path)
    elif path.lower().endswith(".txt"):
        data.raw = load_txt(path)
    else:
        raise FileNotFoundError("File not supported")
    return data
