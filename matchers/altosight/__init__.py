import pandas as pd
import typing
from . import extract
from .. import AbstractMatcher
from .. import timing

def createMatchPair(instanceIdA: str, instanceIdB: str) -> typing.Tuple[str, str]:
    if instanceIdA >= instanceIdB:
        instanceIdA, instanceIdB = instanceIdB, instanceIdA
    return (instanceIdA, instanceIdB)

def removeTransitivity(
    c: str,
    matchPairs: typing.Set[typing.Tuple[str, str]],
    notMatchPairs: typing.Set[typing.Tuple[str, str]],
    modelDict: typing.Dict[str, str]
) -> None:
    cModel = modelDict[c]
    for a, b in notMatchPairs:  # type: str, str
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
    def check(df: pd.DataFrame) -> bool:
        return all(
            col in df.columns
            for col in (
                'name',
                'price',
                'brand',
                'size',
                'instance_id',
            )
        )

    @staticmethod
    @timing('Extract')
    def extract(df: pd.DataFrame) -> None:
        # 将所有数据转为小写
        for col in df.columns:
            if col != 'instance_id':
                df[col] = df[col].str.lower()
        df['name'] = df['name'].apply(
            lambda s: s
                .replace('&nbsp;', ' ')
                .replace('\\n', ' ')
                .strip()
        )
        df['x_size'] = df.apply(extract.size, axis=1)
        df['x_type'] = df.apply(extract.type, axis=1)
        df['x_brand_type'] = df.apply(lambda s: f'{s["brand"]}-{s["x_type"]}', axis=1)
        df['x_sdcard_standard'] = df.apply(extract.sdcardStandard, axis=1)
        df['x_usb_standard'] = df.apply(extract.usbStandard, axis=1)
        df['x_color'] = df.apply(extract.color, axis=1)
        df['x_model'] = df.apply(extract.model, axis=1)

    @staticmethod
    def compare(seriesA: pd.Series, seriesB: pd.Series) -> bool:
        for colVeto in (
            'x_model',
            'x_brand_type',
            'x_size',
            'x_color',
            # 'x_sdcard_standard',
            # 'x_usb_standard',
        ):
            if (
                not pd.isna(seriesA[colVeto]) and
                not pd.isna(seriesB[colVeto]) and
                seriesA[colVeto] != seriesB[colVeto]
            ):
                return False

        # for colSubstr in (
        #     'x_sdcard_standard',
        # ):
        #     if (
        #         not pd.isna(seriesA[colSubstr]) and
        #         not pd.isna(seriesB[colSubstr]) and
        #         not seriesA[colSubstr] in seriesB[colSubstr] and
        #         not seriesB[colSubstr] in seriesA[colSubstr]
        #     ):
        #         return False

        return True

    @classmethod
    @timing('Match')
    def match(cls, df: pd.DataFrame) -> typing.Iterable[typing.Tuple[str, str]]:
        # 和notebook完全一致的做法
        output = []
        for brandType, brandTypeGroup in df.groupby('x_brand_type'):
            print(f'Matching in group "{brandType}"...')
            matchPairs = set() # type: set[tuple[str, str]]
            notMatchPairs = set() # type: set[tuple[str, str]]
            brandTypeGroup.apply(
                lambda seriesA:
                brandTypeGroup.apply(
                    lambda seriesB:
                    seriesA.name < seriesB.name and
                    # cls.compare(seriesA, seriesB) and
                    # output.append((seriesA['instance_id'], seriesB['instance_id'])),
                    (matchPairs if cls.compare(seriesA, seriesB) else notMatchPairs)
                        .add(createMatchPair(seriesA['instance_id'], seriesB['instance_id'])),
                    axis=1
                ),
                axis=1
            )
            # 破坏对比失败的传递性
            modelDict = df[['instance_id','x_model']].set_index('instance_id').to_dict()['x_model'] # type: dict[str, str]
            brandTypeGroup.apply(
                lambda series: removeTransitivity(series['instance_id'], matchPairs, notMatchPairs, modelDict),
                axis=1
            )
            output.extend(matchPairs)
        return output
