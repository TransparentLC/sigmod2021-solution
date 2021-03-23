import pandas as pd

def notebook(seriesA: pd.Series, seriesB: pd.Series) -> bool:
    # 考虑到单位换算和误差，重量有0.2kg之内的误差都是可以接受的
    # if all((
    #     not pd.isna(seriesA['x_weight']),
    #     not pd.isna(seriesB['x_weight']),
    #     abs(seriesA['x_weight'] - seriesB['x_weight']) > .2,
    # )):
    #     return False

    # cA,cB='',''
    # if pd.isna(seriesA['x_cpu_model']):
    #     cA = seriesA['x_cpu_brand']
    # else:
    #     cA = seriesA['x_cpu_model']
    #
    # if pd.isna(seriesB['x_cpu_model']):
    #     cB = seriesB['x_cpu_brand']
    # else:
    #     cB=seriesB['x_cpu_model']
    # if cA!=cB:
    #     return False
    
    if (not pd.isna(seriesA['x_ram_type'])) and (not pd.isna(seriesB['x_ram_type'])):
        if (seriesA['x_ram_type'] not in seriesB['x_ram_type']) and (seriesB['x_ram_type'] not in seriesA['x_ram_type']):
            return False
        
    for colVeto in ('x_model', 'x_cpu_brand', 'x_cpu_model', 'x_cpu_frequency', 'x_ram_capacity'):
        if all((
            not pd.isna(seriesA[colVeto]),
            not pd.isna(seriesB[colVeto]),
            seriesA[colVeto] != seriesB[colVeto],
        )):
            return False

    return True
