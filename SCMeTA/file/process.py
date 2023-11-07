import pandas as pd

from .format import SCData


def load_process_data(name, path) -> SCData:
    process = pd.read_csv(path, index_col=0)
    data = SCData(name)
    data.process = process
    return data
