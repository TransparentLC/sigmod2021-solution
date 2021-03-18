import compare
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
    data['x_cpu_model']=data.apply(extract.cpuModel,axis=1)
    data['x_cpu_frequency'] = data.apply(extract.cpuFrequency, axis=1)
    data['x_ram_capacity'] = data.apply(extract.ramCapacity, axis=1)
    data['x_ram_type'] = data.apply(extract.ramType, axis=1)
    _te = time.perf_counter()
    timeCounter['Extract'] = _te - _ts

    print(data)
    data.to_csv('extract-test.csv', index=False)

    # 对比和输出数据
    _ts = time.perf_counter()
    # 直接往DataFrame里append的话太慢了……
    # 所以这里用list保存
    output = [] # type: list[str, str]
    # 以品牌分组，在每个组里两两比较
    for brand, brandGroup in data.groupby('x_brand'): # type: str, pd.DataFrame
        print(f'Matching in group "{brand}"...')
        for indexA, seriesA in brandGroup.iterrows(): # type: int, pd.Series
            for indexB, seriesB in brandGroup.iterrows():  # type: int, pd.Series
                if indexA >= indexB:
                    continue
                if compare.notebook(seriesA, seriesB):
                    output.append((seriesA['instance_id'], seriesB['instance_id']))
    pd.DataFrame(
        output,
        columns=('left_instance_id', 'right_instance_id'),
        dtype=pd.StringDtype()
    ).to_csv('output.csv', index=False)
    _te = time.perf_counter()
    timeCounter['Output'] = _te - _ts

    te = time.perf_counter()
    timeCounter['Total'] = te - ts
    print('= Time Counter =')
    for k, v in timeCounter.items(): # type: str, float
        print(k, v)
