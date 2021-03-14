import extract
import pandas as pd
import time

if __name__ == '__main__':
    ts = time.perf_counter()

    data = pd.read_csv('datasets/X2.csv', dtype=pd.StringDtype())
    data['x_brand'] = pd.Series(dtype=pd.StringDtype())

    for index, row in data.iterrows():
        # 把所有数据转为小写
        for col in data.columns:
            if not pd.isna(data.loc[index, col]):
                data.loc[index, col] = data.loc[index, col].lower()
        # 通过正则表达式解析信息
        data.loc[index, 'x_brand'] = extract.brand(row)

    print(data)

    te = time.perf_counter()
    print(te - ts)