import pandas as pd
from combat.pycombat import pycombat

from SCMeTA.file import SCData


def combat_batch_correction(data: dict[str, SCData], tags: list[str]) -> dict[str, SCData]:
    # 获取细胞组名和数据框列表
    d_list = []
    for key, value in data.items():
        cell_mat = value.cell_mat.T
        for tag in tags:
            if key in tag:
                cell_mat.columns = [tag for _ in range(len(cell_mat.columns))]
        d_list.append(value.cell_mat.T)

    # 合并所有细胞组数据
    df_expression = pd.concat(d_list, join="inner", axis=1)

    # 创建批次标签列表
    batch = []
    datasets = d_list
    for j in range(len(datasets)):
        batch.extend([j for _ in range(len(datasets[j].columns))])

    # run pyComBat
    df_corrected = pycombat(df_expression, batch)

    start = 0
    end = 0
    # 获取校正后的各细胞组数据
    for key in data.keys():
        d = df_corrected.T
        end += len(data[key].cell_mat.index)
        d = d.iloc[start:end, :]
        d.index = data[key].cell_mat.index
        start = end
        data[key].cell_mat = d
    return data
