import pandas as pd
import numpy as np
from tqdm import tqdm


# DDA analysis

class DDAAnnotation:
    def __init__(self):
        pass

def cal_ppm(mz1: float, mz2: float) -> float:
    """
    Calculate the ppm (parts per million) between two m/z values.
    :param mz1: The first m/z value.
    :param mz2: The second m/z value.
    :return: The ppm value.
    """
    return abs((mz1 - mz2) / mz1) * 1e6


def match_list(mz_list: list, database_list: list, tolerance: int = 5, progress_bar=None) -> list:
    """
    Match the mz_list with the database_list and return the matched list.
    :param mz_list: The mz_list to be matched.
    :param database_list: The database_list to be matched with.
    :param tolerance: The tolerance for matching, default is 5 ppm.
    :param progress_bar: The progress bar to show the progress of the matching.
    :return: The matched list.
    """
    matched_list = []
    for mz in mz_list:
        for db_mz in database_list:
            if cal_ppm(mz, db_mz) < tolerance:
                matched_list.append(db_mz)
                break
    return matched_list

def match_rate(matched_list: list, database_list: list) -> float:
    """
    Calculate the match rate between the matched list and the database list.
    :param matched_list: The matched list.
    :param database_list: The database list.
    :return: The match rate.
    """
    if len(database_list) == 0:
        return 0
    return len(matched_list) / len(database_list)

def