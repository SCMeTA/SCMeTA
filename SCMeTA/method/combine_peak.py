import pandas as pd



def combine_peak(mat: pd.DataFrame):
    # Combine the columns which the difference is less than 0.01
    combined_mat = pd.DataFrame()
    for col in mat.columns:
        if col not in combined_mat.columns:
            # Find the columns that are similar to the current column
            similar_cols = [c for c in mat.columns if abs(float(c) - float(col)) < 0.01]
            # Combine the similar columns by taking the mean
            combined_mat[col] = mat[similar_cols].mean(axis=1)
            # Remove the similar columns from the original matrix
            mat.drop(columns=similar_cols, inplace=True)
    # Add the combined columns to the original matrix
    mat = pd.concat([mat, combined_mat], axis=1)
    # Remove duplicate columns
    mat = mat.loc[:, ~mat.columns.duplicated()]
    # Sort the columns by name
    mat = mat.reindex(sorted(mat.columns), axis=1)
    return mat