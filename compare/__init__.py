import pandas as pd

def notebook(seriesA: pd.Series, seriesB: pd.Series) -> bool:
    # 这些列的数据如果不同就一票否决
    for colVeto in ('x_hdd_capacity', 'x_ssd_capacity', 'x_ram_capacity'):
        if seriesA[colVeto] != seriesB[colVeto]:
            return False

    # 考虑到单位换算和误差，重量有0.2kg之内的误差都是可以接受的
    if all((
        not pd.isna(seriesA['x_weight']),
        not pd.isna(seriesB['x_weight']),
        abs(seriesA['x_weight'] - seriesB['x_weight']) > .2,
    )):
        return False

    # TODO 其他列的对比

    return True