import compare
import extract
import pandas as pd
import time
import typing

# 只是为了保证每一组match中两个id的顺序
def createMatchPair(instanceIdA: str, instanceIdB: str) -> typing.Tuple[str, str]:
    if instanceIdA >= instanceIdB:
        instanceIdA, instanceIdB = instanceIdB, instanceIdA
    return (instanceIdA, instanceIdB)

# 已知A!=B，但是有A==C和B==C的记录，则最后还是会被认为有A==B
# createMatchPair保证了A<B，根据ABC的大小关系有以下几种情况：
# A<B<C 需要去掉A==C和B==C
# A<C<B 需要去掉A==C和C==B
# C<A<B 需要去掉C==A和C==B
# 实际上要彻底破坏传递性的话，相当于在无向图中循环查找并删除所有A到B的路径
# 但是这里先考虑路径长度为2的情况
# 参数c就是上面的C了，通过df.apply调用时可以提供
def removeTransitivity(c: str, matchPairs: set, notMatchPairs: set):
    for a, b in notMatchPairs: # type: str, str
        if a < b and b < c and (a, c) in matchPairs and (b, c) in matchPairs:
            print(a, b, c)
            matchPairs.remove((a, c))
            matchPairs.remove((b, c))
        elif a < c and c < b and (a, c) in matchPairs and (c, b) in matchPairs:
            print(a, c, b)
            matchPairs.remove((a, c))
            matchPairs.remove((c, b))
        elif c < a and a < b and (c, a) in matchPairs and (c, b) in matchPairs:
            print(c, a, b)
            matchPairs.remove((c, a))
            matchPairs.remove((c, b))

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

    # 对比数据
    _ts = time.perf_counter()
    # 直接往DataFrame里append的话太慢了……
    # 把比较成功和失败的一对都记下来
    # 最后需要根据失败的记录删去某些成功的对来破坏传递性（后述）
    output = [] # type: list[tuple[str, str]]
    # 以品牌分组，在每个组里两两比较
    for brand, brandGroup in data.groupby('x_brand'): # type: str, pd.DataFrame
        print(f'Matching in group "{brand}"...')
        matchPairs = set() # type: set[tuple[str, str]]
        notMatchPairs = set() # type: set[tuple[str, str]]
        # for indexA, seriesA in brandGroup.iterrows(): # type: int, pd.Series
        #     for indexB, seriesB in brandGroup.iterrows():  # type: int, pd.Series
        #         if indexA >= indexB:
        #             continue
        #         if compare.notebook(seriesA, seriesB):
        #             output.append((seriesA['instance_id'], seriesB['instance_id']))
        brandGroup.apply(
            lambda seriesA:
                brandGroup.apply(
                    lambda seriesB:
                        # series.name就是每一行的index
                        # 短路求值，这个条件成立才会执行比较
                        seriesA.name < seriesB.name and
                        # 至于这个返回什么已经不重要了
                        (matchPairs if compare.notebook(seriesA, seriesB) else notMatchPairs).add(createMatchPair(seriesA['instance_id'], seriesB['instance_id'])),
                    axis=1
                ),
            axis=1
        )
        # 破坏对比失败的传递性
        brandGroup.apply(
            lambda series: removeTransitivity(series['instance_id'], matchPairs, notMatchPairs),
            axis=1
        )
        output.extend(matchPairs)
    _te = time.perf_counter()
    timeCounter['Match'] = _te - _ts

    _ts = time.perf_counter()
    pd.DataFrame(
        output,
        columns=('left_instance_id', 'right_instance_id'),
        dtype=pd.StringDtype()
    ).to_csv('output.csv', index=False)
    _te = time.perf_counter()
    timeCounter['Output csv'] = _te - _ts

    te = time.perf_counter()
    timeCounter['Total'] = te - ts
    print('= Time Counter =')
    for k, v in timeCounter.items(): # type: str, float
        print(f'{k:<{max(len(x) for x in timeCounter.keys())}} {v:.4f}s {v / timeCounter["Total"] * 100:.2f}%')
