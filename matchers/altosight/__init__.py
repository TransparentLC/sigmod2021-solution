import pandas as pd
import typing
from . import extract
from .. import AbstractMatcher
from .. import timing

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
        df['name'] = df['name'].apply(lambda s: s.replace('&nbsp;', ' '))
        df['x_size'] = df.apply(extract.size, axis=1)
        df['x_type'] = df.apply(extract.type, axis=1)
        df['x_brand_type'] = df.apply(lambda s: f'{s["brand"]}-{s["x_type"]}', axis=1)

    @staticmethod
    def compare(seriesA: pd.Series, seriesB: pd.Series) -> bool:
        return False

    @classmethod
    @timing('Match')
    def match(cls, df: pd.DataFrame) -> typing.Iterable[typing.Tuple[str, str]]:
        return ()
