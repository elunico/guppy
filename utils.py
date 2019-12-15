import os
import subprocess
import sys

user_url = 'https://api.github.com/users/{user}'
usr_repos_url = 'https://api.github.com/users/{user}/{repo}'
repo_url = 'https://api.github.com/repos/{user}/{repo}'
languages_url = 'https://api.github.com/repos/{user}/{repo}/languages'

usage = "Usage: {0} mode. Try '{0} help' for help".format(sys.argv[0])

try:
    if 'COLUMNS' in os.environ:
        CONSOLE_WIDTH = int(os.environ['COLUMNS'])
    elif os.system('stty size > /dev/null 2>&1') == 0:
        CONSOLE_WIDTH = int(subprocess.getstatusoutput(
            'stty size')[1].split()[1])
    else:
        CONSOLE_WIDTH = 80
except (IndexError, ValueError, AttributeError):
    CONSOLE_WIDTH = 80


def boxed(msg, center=CONSOLE_WIDTH - 4):
    msg = msg.center(center)
    size = len(msg) + 4
    print('-' * size)
    print("| {} |".format(msg))
    print('-' * size)
