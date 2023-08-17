from .knn import knn_impute


def fill_mat(mat, method: str):
    if method == "knn":
        return knn_impute(mat)
    elif method == "zero":
        return mat.fillna(0)
    elif method == "none":
        return mat
    else:
        raise KeyError("Invalid method")