from sklearn.impute import KNNImputer
import pandas as pd


def knn_impute(data):
    # Remove non numeric columns
    data = data.dropna(axis=1, how="all")
    imputer = KNNImputer(n_neighbors=5)
    imputed_data = imputer.fit_transform(data)
    imputed_data_df = pd.DataFrame(imputed_data)
    imputed_data_df.columns = data.columns
    imputed_data_df.index = data.index
    return imputed_data_df
