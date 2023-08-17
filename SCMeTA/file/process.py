import pandas as pd

from .format import MSData


def load_process_data(name, path) -> MSData:
    process = pd.read_csv(path, index_col=0)
    data = MSData(name)
    data.process = process
    return data
