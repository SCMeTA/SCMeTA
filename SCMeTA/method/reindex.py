from SCMeTA.file import SCData
import numpy as np


def reindex_mat(data: SCData):
    new_index = np.arange(data.mat.shape[0])
    data.mat.index = new_index
    return data.mat
