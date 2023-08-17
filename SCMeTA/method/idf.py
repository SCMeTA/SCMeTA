import pandas as pd
import numpy as np


def tfidf(mat: pd.DataFrame) -> pd.DataFrame:
    data = mat.replace(0, np.nan)
    total_intensity = data.sum(axis=1)
    tf = data.divide(total_intensity, axis=0)
    idf = np.log(data.shape[0] / data.count())
    tfidf = tf * idf
    return tfidf


if __name__ == "__main__":
    mat = pd.read_csv(
        "/Users/Estrella/Developer/CyESI/Process/Data/idf-test.csv", index_col=0
    )
    result = tfidf(mat)
    # loc 760.58
