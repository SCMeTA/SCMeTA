import numpy as np
import pandas as pd


def discriminate(
    data_list: dict[str, pd.DataFrame], method: str, n_components: int = 2
) -> np.ndarray:
    """
    Discriminate data by different methods.
    Args:
        data_list: A dict of dataframes or a MSProcess object.
        method: The method to discriminate data.
        n_components: The number of components to keep.

    Returns:
        A numpy array of the result of the method.
    """
    from sklearn.manifold import TSNE
    from sklearn.decomposition import PCA, KernelPCA
    from umap import UMAP

    METHODS = {
        "pca": PCA,
        "kpca": KernelPCA,
        "tsne": TSNE,
        "umap": UMAP,
    }
    full = pd.concat(data_list.values(), axis=0).fillna(0)
    reduce = METHODS[method](n_components=n_components)
    return reduce.fit_transform(full)


def to_mat(
        full: np.ndarray, cell_range: dict[str, int], n_components: int = 2
) -> dict[str, pd.DataFrame]:
    """
    Convert the result of discriminate to a dataframe.
    Args:
        full: The result of discriminate.
        cell_range: The range of each cell.

    Returns:
        A dataframe of the result of discriminate.
    """
    data_list = {}
    start = 0
    end = 0
    for cell, cell_count in cell_range.items():
        end += cell_count
        if n_components == 1:
            col = ["x"]
            value = full[start:end, 0]
        elif n_components == 2:
            col = ["x", "y"]
            value = full[start:end, 0:2]
        elif n_components == 3:
            col = ["x", "y", "z"]
            value = full[start:end, 0:3]
        else:
            raise ValueError("Invalid n_components")
        data_list[cell] = pd.DataFrame(
            value[start:end], columns=col, index=range(cell_count)
        )
        start += cell_count
    return data_list
