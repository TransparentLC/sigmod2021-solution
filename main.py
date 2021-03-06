import matchers
import matchers.altosight
import matchers.notebook
import matchers.notebook2
import pandas as pd
import os
import sys
import typing

IS_SUBMISSION = '--submission' in sys.argv

if __name__ == '__main__':
    if IS_SUBMISSION:
        print('\033[92mRunning in submission mode!\033[39m')
    else:
        print('\033[96mNot running in submission mode...\033[39m')

    datasetPaths = (
        'datasets/X2.csv',
        'datasets/X3.csv',
        'datasets/X4.csv',
    ) if IS_SUBMISSION else (
        # 'datasets/X2.csv',
        # 'datasets/X3.csv',
        'datasets/X4.csv',
    )
    output = [] # type: list[tuple[str, str]]

    for datasetPath in datasetPaths:
        print(f'Matching {datasetPath}')
        data = pd.read_csv(datasetPath, dtype=pd.StringDtype()) # type: pd.DataFrame

        # 获取可用的matcher
        matcher = None # type: matchers.AbstractMatcher
        for matcherName in (
            'altosight',
            'notebook2',
            'notebook',
        ):
            m = getattr(matchers, matcherName).matcher # type: matchers.AbstractMatcher
            if m.check(data):
                matcher = m
                print(f'Using matcher: {matcherName}')
                break
        if matcher is None:
            raise Exception('Failed to find a matcher')

        # 提取特征
        matcher.extract(data)
        data.to_csv(f'extract-{os.path.splitext(os.path.split(datasetPath)[1])[0]}.csv', index=False)

        # 获取结果并写入output
        output.extend(matcher.match(data))

    pd.DataFrame(
        output,
        columns=('left_instance_id', 'right_instance_id'),
        dtype=pd.StringDtype()
    ).to_csv('output.csv', index=False)
