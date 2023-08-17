import pandas as pd

from .load import METABOLITE, PARAMETERS

if PARAMETERS.lock:
    if METABOLITE.online:
        INCLUDE_LIST = pd.read_csv(METABOLITE.include)["mz"].tolist()
        EXCLUDE_LIST = pd.read_csv(METABOLITE.exclude)["mz"].tolist()
    else:
        INCLUDE_LIST = pd.read_csv(METABOLITE.include)["mz"].tolist()
        EXCLUDE_LIST = pd.read_csv(METABOLITE.exclude)["mz"].tolist()
else:
    INCLUDE_LIST = None
    EXCLUDE_LIST = None
