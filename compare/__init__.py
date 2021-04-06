import pandas as pd

# 以下每一组内的笔记本型号可以当成同一个
# 这是翻了一大堆False Negative记录之后得出的结论
equalNotebookModelGroups = (
    set(('x220 4287', 'x220 4290', 'x220 4291')),
    set(('x130 2338', 'x130 2339')),
    set(('x130 0622', 'x130 0627')),
    set(('x230 2320', 'x230 3435')),
    set(('v7-482', 'v7-582')),
    set(('i5547-3751slv', 'i5547-3753slv')),
)

def notebookGetEqualModelName(model: str) -> str:
    for g in equalNotebookModelGroups:
        if model in g:
            return tuple(g)[0]
    return model

def notebook(seriesA: pd.Series, seriesB: pd.Series) -> bool:
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
        if all((
            not pd.isna(seriesA[colVeto]),
            not pd.isna(seriesB[colVeto]),
            seriesA[colVeto] != seriesB[colVeto],
        )):
            return False

    # 由于False Negative中出现了一些RAM为2GB/4GB的Lenovo ThinkPad X220 4090/4291
    # 所以把这个例外加上
    if all((
        not pd.isna(seriesA['x_ram_capacity']),
        not pd.isna(seriesB['x_ram_capacity']),
        not all((
            not pd.isna(seriesA['x_model']) and seriesA['x_model'].startswith('x220 429'),
            not pd.isna(seriesB['x_model']) and seriesB['x_model'].startswith('x220 429'),
        )),
        seriesA['x_ram_capacity'] != seriesB['x_ram_capacity'],
    )):
        return False

    return True
