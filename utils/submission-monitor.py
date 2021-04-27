import configparser
import re
import requests
import subprocess
import time
from urllib import parse

# File contents of "account.ini":
# [Account]
# Username = ******
# Password = ******
config = configparser.ConfigParser()
config.read('account.ini')

# Download snoretoast from:
# https://github.com/KDE/snoretoast
SNORETOAST_PATH = r"C:\Windows\snoretoast.exe"
INTERVAL = 60
USERNAME = config['Account']['Username']
PASSWORD = config['Account']['Password']

submissionStatus = {
    'currentPosition': 0,
    'lastScore': 0,
}

s = requests.session()
while True:
    try:
        r = s.get(
            'https://dbgroup.ing.unimo.it/sigmod21contest/dashboard/dashboard.php',
            allow_redirects=False
        )
        r.raise_for_status()
        if r.status_code == 302:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'Making login requests')
            r = s.post(
                'https://dbgroup.ing.unimo.it/sigmod21contest/dashboard/login.php',
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                data=parse.urlencode({
                    'name': USERNAME,
                    'password': PASSWORD,
                    'Submit': 'Login',
                })
            )
            r.raise_for_status()

        lastPosition = submissionStatus['currentPosition']
        lastScore = float(re.search(r'\b(0\.\d{3})\b', r.text).group(1))
        if 'You have a pending submission.' in r.text:
            match = re.search(r'The submission is in position (\d+) of the evaluation queue', r.text)
            currentPosition = int(match.group(1))
        else:
            currentPosition = 0
        submissionStatus['currentPosition'] = currentPosition
        submissionStatus['lastScore'] = lastScore
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), submissionStatus)

        toastEnable = lastPosition != currentPosition
        if currentPosition:
            toastTitle = 'New submission pending'
            toastMessage = f'The submission is in position {currentPosition} of the evaluation queue'
        else:
            toastTitle = 'Evaluation complete!'
            toastMessage = f'The F-score of the last submission is {lastScore}'
        if toastEnable:
            subprocess.run((
                SNORETOAST_PATH,
                '-t',
                toastTitle,
                '-m',
                toastMessage,
            ))
    except Exception as ex:
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), type(ex).__name__, ex)

    time.sleep(INTERVAL)
