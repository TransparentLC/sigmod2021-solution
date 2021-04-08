import pandas as pd
import typing
from . import extract
from .. import AbstractMatcher
from .. import timing

# 只是为了保证每一组match中两个id的顺序
def createMatchPair(instanceIdA: str, instanceIdB: str) -> typing.Tuple[str, str]:
    if instanceIdA >= instanceIdB:
        instanceIdA, instanceIdB = instanceIdB, instanceIdA
    return (instanceIdA, instanceIdB)

def getEqualModelName(model: str) -> str:
    for g in (
        {'x220 4287', 'x220 4290', 'x220 4291'},
        {'x130 2338', 'x130 2339'},
        {'x130 0622', 'x130 0627'},
        {'x230 2320', 'x230 3435'},
        {'v7-482', 'v7-582'},
        {'i5547-3751slv', 'i5547-3753slv'},
    ):
        if model in g:
            return tuple(g)[0]
    return model

# 已知A!=B，但是有A==C和B==C的记录，则最后还是会被认为有A==B
# createMatchPair保证了A<B，根据ABC的大小关系有以下几种情况：
# A<B<C 需要去掉A==C和B==C
# A<C<B 需要去掉A==C和C==B
# C<A<B 需要去掉C==A和C==B
# 实际上要彻底破坏传递性的话，相当于在无向图中循环查找并删除所有A到B的路径
# 但是这里先考虑路径长度为2的情况
# 参数c就是上面的C了，通过df.apply调用时可以提供

# modelDict是根据instance_id查找x_model用的
# 如果型号相同就不删除路径吗？
# 仍然删除：自测F值0.99 ↑ 上传F值0.911 ↓ (commit 0ffff35)
# 不删除了：自测F值0.95 ↓ 上传F值0.919 ↑ (commit 5008bb7)
# 有别的修改的时候可以顺便改一改这里试试看……
def removeTransitivity(
    c: str,
    matchPairs: typing.Set[typing.Tuple[str, str]],
    notMatchPairs: typing.Set[typing.Tuple[str, str]],
    modelDict: typing.Dict[str, str]
) -> None:
    cModel = modelDict[c]
    for a, b in notMatchPairs: # type: str, str
        aModel = modelDict[a]
        bModel = modelDict[b]
        if a < b and b < c and (a, c) in matchPairs and (b, c) in matchPairs:
            if aModel != cModel:
                matchPairs.remove((a, c))
            if bModel != cModel:
                matchPairs.remove((b, c))
        elif a < c and c < b and (a, c) in matchPairs and (c, b) in matchPairs:
            if aModel != cModel:
                matchPairs.remove((a, c))
            if cModel != bModel:
                matchPairs.remove((c, b))
        elif c < a and a < b and (c, a) in matchPairs and (c, b) in matchPairs:
            if cModel != aModel:
                matchPairs.remove((c, a))
            if cModel != bModel:
                matchPairs.remove((c, b))

class matcher(AbstractMatcher):
    @staticmethod
    @timing('Check')
    def check(df: pd.DataFrame) -> bool:
        return all(
            col in df.columns
            for col in (
                'instance_id',
                'brand',
                'cpu_brand',
                'cpu_model',
                'cpu_type',
                'cpu_frequency',
                'ram_capacity',
                'ram_type',
                'ram_frequency',
                'hdd_capacity',
                'ssd_capacity',
                'weight',
                'dimensions',
                'title',
            )
        )

    @staticmethod
    @timing('Extract')
    def extract(df: pd.DataFrame) -> None:
        # 将所有数据转为小写
        for col in df.columns:
            df[col] = df[col].str.lower()
        # 通过正则表达式解析信息
        df['x_brand'] = df.apply(extract.brand, axis=1)
        df['x_weight'] = df.apply(extract.weight, axis=1)
        df[['x_hdd_capacity', 'x_ssd_capacity']] = df.apply(extract.diskCapacity, axis=1)
        df['x_cpu_brand'] = df.apply(extract.cpuBrand, axis=1)
        df['x_cpu_model'] = df.apply(extract.cpuModel,axis=1)
        df['x_cpu_frequency'] = df.apply(extract.cpuFrequency, axis=1)
        df['x_ram_capacity'] = df.apply(extract.ramCapacity, axis=1)
        df['x_ram_type'] = df.apply(extract.ramType, axis=1)
        df['x_win_type'] = df.apply(extract.winType, axis=1)
        df['x_model'] = df.apply(extract.model, axis=1)
        df['x_model'] = df['x_model'].apply(getEqualModelName)
        df['x_size'] = df.apply(extract.size, axis=1)

    @staticmethod
    def compare(seriesA: pd.Series, seriesB: pd.Series) -> bool:
        # if seriesA['instance_id'] == '' and seriesB['instance_id'] == '':
        #     print('debug')

        # 考虑到单位换算和误差，重量有0.2kg之内的误差都是可以接受的
        # 这个还是不靠谱啊……
        # if all((
        #     not pd.isna(seriesA['x_weight']),
        #     not pd.isna(seriesB['x_weight']),
        #     abs(seriesA['x_weight'] - seriesB['x_weight']) > .2,
        # )):
        #     return False

        if (not pd.isna(seriesA['x_ram_type'])) and (not pd.isna(seriesB['x_ram_type'])):
            if (seriesA['x_ram_type'] not in seriesB['x_ram_type']) and (seriesB['x_ram_type'] not in seriesA['x_ram_type']):
                return False

        for colVeto in ('x_model', 'x_cpu_brand', 'x_cpu_model', 'x_cpu_frequency'):
            if (
                not pd.isna(seriesA[colVeto]) and
                not pd.isna(seriesB[colVeto]) and
                seriesA[colVeto] != seriesB[colVeto]
            ):
                return False

        # 由于False Negative中出现了一些RAM为2GB/4GB的Lenovo ThinkPad X220 4090/4291
        # 所以把这个例外加上
        if (
            not pd.isna(seriesA['x_ram_capacity']) and
            not pd.isna(seriesB['x_ram_capacity']) and
            not (
                not pd.isna(seriesA['x_model']) and seriesA['x_model'].startswith('x220 429') and
                not pd.isna(seriesB['x_model']) and seriesB['x_model'].startswith('x220 429')
            ) and
            seriesA['x_ram_capacity'] != seriesB['x_ram_capacity']
        ):
            return False

        return True

    @classmethod
    @timing('Match')
    def match(cls, df: pd.DataFrame) -> typing.Iterable[typing.Tuple[str, str]]:
        # 直接往DataFrame里append的话太慢了……
        # 把比较成功和失败的一对都记下来
        # 最后需要根据失败的记录删去某些成功的对来破坏传递性（后述）
        output = [] # type: list[tuple[str, str]]
        # 以品牌分组，在每个组里两两比较
        for brand, brandGroup in df.groupby('x_brand'): # type: str, pd.DataFrame
            print(f'Matching in group "{brand}"...')
            # 按照型号进行聚类
            # modelCluster = {
            #     'model-1': [
            #         {
            #             'feature': pd.Series with x_* cols,
            #             'instance': set(('instance-1', 'instance-2', ...))
            #         },
            #         ...
            #     ],
            #     'model-2': ...
            # }

            # modelCluster = dict() # type: dict[str, list[Cluster]]
            # for index, series in brandGroup.iterrows(): # type: int, pd.Series
            #     if series['x_model'] not in modelCluster:
            #         modelCluster[series['x_model']] = []
            #     merged = False
            #     for cluster in modelCluster[series['x_model']]:
            #         if compare.notebook(series, cluster.featureSeries):
            #             merged = True
            #             cluster.mergeInstanceSeries(series)
            #             break
            #     if not merged:
            #         newCluster = Cluster(extract.customNotebookFeatures)
            #         newCluster.mergeInstanceSeries(series)
            #         modelCluster[series['x_model']].append(newCluster)

            # 尝试合并某些cluster
            # mergedCluster = [] # type: list[Cluster]
            # for k, v in modelCluster.items(): # type: str, list[Cluster]
            #     for cluster in v:
            #         merged = False
            #         for c in mergedCluster:
            #             if compare.notebook(c.featureSeries, cluster.featureSeries):
            #                 merged = True
            #                 c.instance.update(cluster.instance)
            #                 break
            #         if not merged:
            #             mergedCluster.append(cluster)

            # 把每个cluster的结果写入output
            # for cluster in mergedCluster:
            #     instances = tuple(cluster.instance)
            #     for i in range(len(instances)):
            #         for j in range(len(instances)):
            #             if i > j:
            #                 output.append((instances[i], instances[j]))

            matchPairs = set() # type: set[tuple[str, str]]
            notMatchPairs = set() # type: set[tuple[str, str]]
            brandGroup.apply(
                lambda seriesA:
                    brandGroup.apply(
                        lambda seriesB:
                            # series.name就是每一行的index
                            # 短路求值，这个条件成立才会执行比较
                            seriesA.name < seriesB.name and
                            # 至于这个返回什么已经不重要了
                            (matchPairs if cls.compare(seriesA, seriesB) else notMatchPairs)
                                .add(createMatchPair(seriesA['instance_id'], seriesB['instance_id'])),
                        axis=1
                    ),
                axis=1
            )
            # 破坏对比失败的传递性
            modelDict = df[['instance_id','x_model']].set_index('instance_id').to_dict()['x_model'] # type: dict[str, str]
            brandGroup.apply(
                lambda series: removeTransitivity(series['instance_id'], matchPairs, notMatchPairs, modelDict),
                axis=1
            )
            output.extend(matchPairs)
        return output
