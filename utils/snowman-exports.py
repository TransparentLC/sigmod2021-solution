import csv
import requests
import json
import os

groundTruthId = int(input('Ground truth experiment ID: '))
mockSolutionId = int(input('Mock solution experiment ID: '))

exportFolder = f'snowman-exports/({groundTruthId}, {mockSolutionId})'
if not os.path.isdir('snowman-exports'):
    os.mkdir('snowman-exports')
if os.path.exists(exportFolder):
    print(f'Export folder "{exportFolder}" exists, exitting.')
    exit(1)
os.mkdir(exportFolder)

r = requests.get(
    f'http://localhost:8123/api/v1/benchmark/{groundTruthId}/{mockSolutionId}/metrics'
)
r.raise_for_status()
data = r.json() # type: list[dict]
with open(f'{exportFolder}/metrics.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(f'{d["name"]}: {d["value"]}' for d in data))

for metricName, groundTruthCondition, mockSolutionCondition in (
    ('true-positive', True, True),
    ('false-positive', False, True),
    ('false-negative', True, False),
    # ('true-negative', False, False),
):
    print(f'Getting {metricName} count... ', end='')
    r = requests.post(
        'http://localhost:8123/api/v1/benchmark/experiment-intersection/pair-counts',
        headers={
            'Content-Type': 'application/json',
        },
        data=json.dumps([
            {
                'experimentId': groundTruthId,
            },
            {
                'experimentId': mockSolutionId,
            },
        ])
    )
    r.raise_for_status()
    data = r.json()
    numberRows = 0
    for d in data:
        if len(d['experiments']) == 2 and (
            (
                d['experiments'][0]['experimentId'] == groundTruthId and
                d['experiments'][0]['predictedCondition'] == groundTruthCondition and
                d['experiments'][1]['experimentId'] == mockSolutionId and
                d['experiments'][1]['predictedCondition'] == mockSolutionCondition
            ) or (
                d['experiments'][1]['experimentId'] == groundTruthId and
                d['experiments'][1]['predictedCondition'] == groundTruthCondition and
                d['experiments'][0]['experimentId'] == mockSolutionId and
                d['experiments'][0]['predictedCondition'] == mockSolutionCondition
            )
        ):
            numberRows = d['numberRows']
    print(numberRows)

    startAt = 0
    limit = 1000
    headerWritten = False
    with open(f'{exportFolder}/{metricName}.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        while startAt < numberRows:
            print(f'Writing {metricName} records {startAt}-{min(startAt + limit, numberRows)}')
            r = requests.post(
                f'http://localhost:8123/api/v1/benchmark/experiment-intersection/records?startAt={startAt}&limit={limit}',
                headers={
                    'Content-Type': 'application/json',
                },
                data=json.dumps([
                    {
                        'experimentId': groundTruthId,
                        'predictedCondition': groundTruthCondition,
                    },
                    {
                        'experimentId': mockSolutionId,
                        'predictedCondition': mockSolutionCondition,
                    },
                ])
            )
            r.raise_for_status()
            data = r.json() # type: dict[str, list]
            if not headerWritten:
                writer.writerow(data['header'])
                headerWritten = True
            writer.writerows(data['data'])
            startAt += limit
