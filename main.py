import extract
import pandas as pd
import time

if __name__ == '__main__':
    ts = time.perf_counter()

    data = pd.read_csv('datasets/X2.csv', dtype=pd.StringDtype())
    data['x_brand'] = pd.Series(dtype=pd.StringDtype())
    data['x_weight'] = pd.Series(dtype=pd.Float64Dtype())
    data['x_hdd_capacity'] = pd.Series(dtype=pd.Int32Dtype())
    data['x_ssd_capacity'] = pd.Series(dtype=pd.Int32Dtype())
    data['x_cpuBrand'] = pd.Series(dtype=pd.StringDtype())
    data['x_cpuFrequency']=pd.Series(dtype=pd.StringDtype())
    data['x_ramCapacity']=pd.Series(dtype=pd.StringDtype())
    data['x_ramType']=pd.Series(dtype=pd.StringDtype())

    # 把所有数据转为小写
    for index, row in data.iterrows():
        for col in data.columns:
            if not pd.isna(data.loc[index, col]):
                data.loc[index, col] = data.loc[index, col].lower()

    # 通过正则表达式解析信息
    for index, row in data.iterrows():
        data.loc[index, 'x_brand'] = extract.brand(row)
        data.loc[index, 'x_weight'] = extract.weight(row)
        data.loc[index, 'x_hdd_capacity'], data.loc[index, 'x_ssd_capacity'] = extract.diskCapacity(row)
        data.loc[index,'x_cpuBrand']=extract.cpuBrand(row)
        data.loc[index,'x_cpuFrequency']=extract.cpuFrequency(row)
        data.loc[index,'x_ramCapacity']=extract.ramCapacity(row)
        data.loc[index,'x_ramType'] = extract.ramType(row)

    print(data)
    data.to_csv('extract-test.csv')
    
    te = time.perf_counter()
    print(te - ts)
