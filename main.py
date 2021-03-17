import extract
import pandas as pd
import time

if __name__ == '__main__':
    timeCounter = dict()

    ts = time.perf_counter()

    _ts = time.perf_counter()
    data = pd.read_csv('datasets/X2.csv', dtype=pd.StringDtype()) # type: pd.DataFrame
    _te = time.perf_counter()
    timeCounter['Read csv'] = _te - _ts

    # 把所有数据转为小写
    _ts = time.perf_counter()
    for col in data.columns:
        data[col] = data[col].str.lower()
    _te = time.perf_counter()
    timeCounter['Lowercase'] = _te - _ts

    # 通过正则表达式解析信息
    _ts = time.perf_counter()
    data['x_brand'] = data.apply(extract.brand, axis=1)
    data['x_weight'] = data.apply(extract.weight, axis=1)
    data[['x_hdd_capacity', 'x_ssd_capacity']] = data.apply(extract.diskCapacity, axis=1)
    data['x_cpu_brand'] = data.apply(extract.cpuBrand, axis=1)
    data['x_cpu_frequency'] = data.apply(extract.cpuFrequency, axis=1)
    data['x_ram_capacity'] = data.apply(extract.ramCapacity, axis=1)
    data['x_ram_type'] = data.apply(extract.ramType, axis=1)
    _te = time.perf_counter()
    timeCounter['Extract'] = _te - _ts

    print(data)
    data.to_csv('extract-test.csv')
    
    te = time.perf_counter()
    timeCounter['Total'] = te - ts
    print('= Time Counter =')
    for k, v in timeCounter.items(): # type: str, float
        print(k, v)
