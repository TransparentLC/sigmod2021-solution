import pandas as pd
import typing
from .. import AbstractMatcher
from .. import timing

# TODO

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
        pass

    @staticmethod
    def compare(seriesA: pd.Series, seriesB: pd.Series) -> bool:
        return False

    @classmethod
    @timing('Match')
    def match(cls, df: pd.DataFrame) -> typing.Iterable[typing.Tuple[str, str]]:
        return ()
