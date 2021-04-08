import abc
import functools
import pandas as pd
import time
import typing

def timing(name: str = 'Time') -> typing.Callable:
    '''
    用于计时的函数装饰器
    '''
    def decorator(func: typing.Callable) -> typing.Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ts = time.perf_counter()
            result = func(*args, **kwargs)
            te = time.perf_counter()
            print(f'{name}: {te - ts:.3f}s')
            return result
        return wrapper
    return decorator

class AbstractMatcher(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def check(df: pd.DataFrame) -> bool:
        '''
        检查这个DataFrame是否可以使用当前matcher
        '''
        pass

    @staticmethod
    @abc.abstractmethod
    def extract(df: pd.DataFrame) -> None:
        '''
        对DataFrame中的每一行提取各种特征
        '''
        pass

    @staticmethod
    @abc.abstractmethod
    def compare(seriesA: pd.Series, seriesB: pd.Series) -> bool:
        '''
        对DataFrame中的两行进行比较，返回是否可以当成同一产品
        '''
        pass

    @classmethod
    @abc.abstractmethod
    def match(cls, df: pd.DataFrame) -> typing.Iterable[typing.Tuple[str, str]]:
        '''
        从提取特征后的DataFrame中找到所有可以表示同一实体的两个ID组成的对
        '''
        pass
