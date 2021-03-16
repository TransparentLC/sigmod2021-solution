import extract
import pandas as pd
import time

if __name__ == '__main__':
    ts = time.perf_counter()

    data = pd.read_csv('datasets/X2.csv', dtype=pd.StringDtype())
    data['x_brand'] = pd.Series(dtype=pd.StringDtype())
    data['x_weight'] = pd.Series(dtype=pd.Float32Dtype()) # pandas=1.0.0报错，我运行的时候删了，默认应该就是float64
    data['x_cpuBrand'] = pd.Series(dtype=pd.StringDtype())

    # 把所有数据转为小写
    for index, row in data.iterrows():
        for col in data.columns:
            if not pd.isna(data.loc[index, col]):
                data.loc[index, col] = data.loc[index, col].lower()

    # 通过正则表达式解析信息
    for index, row in data.iterrows():
        data.loc[index, 'x_brand'] = extract.brand(row)
        data.loc[index, 'x_weight'] = extract.weight(row)
        data.loc[index,'x_cpuBrand']=extract.cpuBrand(row)

    print(data)
    #data.to_csv('test.csv')
    
    te = time.perf_counter()
    print(te - ts)
