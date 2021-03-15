import extract
import pandas as pd
import time

if __name__ == '__main__':
    ts = time.perf_counter()

    data = pd.read_csv('datasets/X2.csv', dtype=pd.StringDtype())
    data['x_brand'] = pd.Series(dtype=pd.StringDtype())
    data['x_weight'] = pd.Series(dtype=pd.Float32Dtype())

    # 把所有数据转为小写
    for index, row in data.iterrows():
        for col in data.columns:
            if not pd.isna(data.loc[index, col]):
                data.loc[index, col] = data.loc[index, col].lower()

    # 通过正则表达式解析信息
    for index, row in data.iterrows():
        data.loc[index, 'x_brand'] = extract.brand(row)
        data.loc[index, 'x_weight'] = extract.weight(row)

    print(data)

    te = time.perf_counter()
    print(te - ts)
