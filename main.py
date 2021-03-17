import extract
import pandas as pd
import time

if __name__ == '__main__':
    ts = time.perf_counter()

    data = pd.read_csv('datasets/X2.csv', dtype=pd.StringDtype())
    data['x_brand'] = pd.Series(dtype=pd.StringDtype())
    data['x_weight'] = pd.Series(dtype=pd.Float32Dtype())
    data['x_hdd_capacity'] = pd.Series(dtype=pd.Int32Dtype())
    data['x_ssd_capacity'] = pd.Series(dtype=pd.Int32Dtype())
    data['x_cpu_brand'] = pd.Series(dtype=pd.StringDtype())
    data['x_cpu_frequency']=pd.Series(dtype=pd.StringDtype())
    data['x_ram_capacity']=pd.Series(dtype=pd.StringDtype())
    data['x_ram_type']=pd.Series(dtype=pd.StringDtype())

    # 把所有数据转为小写
    for index, row in data.iterrows():
        for col in data.columns:
            if not pd.isna(data.loc[index, col]):
                data.loc[index, col] = data.loc[index, col].lower()

    # 计算解析和写入数据的时间
    timeExtract = 0
    timeModifyData = 0

    # 通过正则表达式解析信息
    for index, row in data.iterrows():
        _ts = time.perf_counter()
        brand = extract.brand(row)
        weight = extract.weight(row)
        diskCapacity = extract.diskCapacity(row)
        cpuBrand = extract.cpuBrand(row)
        cpuFrequency = extract.cpuFrequency(row)
        ramCapacity = extract.ramCapacity(row)
        ramType = extract.ramType(row)
        _te = time.perf_counter()
        timeExtract += _te - _ts

        _ts = time.perf_counter()
        data.loc[index, 'x_brand'] = brand
        data.loc[index, 'x_weight'] = weight
        data.loc[index, 'x_hdd_capacity'], data.loc[index, 'x_ssd_capacity'] = diskCapacity
        data.loc[index,'x_cpu_brand'] = cpuBrand
        data.loc[index,'x_cpu_frequency'] = cpuFrequency
        data.loc[index,'x_ram_capacity'] = ramCapacity
        data.loc[index,'x_ram_type'] = ramType
        _te = time.perf_counter()
        timeModifyData += _te - _ts

    print(data)
    data.to_csv('extract-test.csv')
    
    te = time.perf_counter()
    print('Extract time:', timeExtract)
    print('Modify data time:', timeModifyData)
    print('Total time:', te - ts)
