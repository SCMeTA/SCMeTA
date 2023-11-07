import os

from SCMeTA.accelerate import MultiThreader

from .thermo import load_thermo_data
from .process import load_process_data
from .waters import load_waters_data
from .format import *
from .database import load_from_database

FUNC_DICT = {
    "thermo": load_thermo_data,
    "process": load_process_data,
    "waters": load_waters_data,
}

SUFFIX_DICT = {
    "thermo": [".raw", ".txt"],
    "process": [".csv"],
    "waters": [".wiff", ".txt"],
}


def is_type(path: str, data_type: str) -> bool:
    suffix = os.path.splitext(path)[1]
    return suffix.lower() in SUFFIX_DICT[data_type]


def get_name_from_path(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]


def path_from_database(path: str) -> str:
    base_path = ".Database/cyesi"
    return os.path.join(base_path, path)


def read_files_in_parallel(paths, names = None, data_type: str = "thermo") -> dict[str, SCData]:
    if names is None:
        names = [get_name_from_path(path) for path in paths]
    args = [(name, path) for name, path in zip(names, paths)]
    mt = MultiThreader()
    results = mt.run(FUNC_DICT[data_type], args)
    return results


def load_data(
    path: str | dict, name: str | None = None, data_type: str = "thermo"
) -> dict[str, SCData]:
    if isinstance(path, str):
        if os.path.isdir(path):
            files = os.listdir(path)
            paths = [os.path.join(path, file) for file in files if is_type(file, data_type)]
            return read_files_in_parallel(paths=paths, data_type=data_type)
        elif os.path.isfile(path) and is_type(path, data_type):
            if name is None:
                name = get_name_from_path(path)
            return {name: FUNC_DICT[data_type](name, path)}
        else:
            raise ValueError("Please provide a valid path")
    elif isinstance(path, dict):
        paths = [path_from_database(path) for path in path.values()]
        results = read_files_in_parallel(paths=paths, names=path.keys(), data_type=data_type)
        return results


