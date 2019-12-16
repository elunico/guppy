import os
import subprocess
import sys
import dateutil.parser
from colors import *

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
    items = msg.splitlines()
    print('-' * CONSOLE_WIDTH)
    for line in items:
        line = line.center(center)
        print("| {} |".format(line))
    print('-' * CONSOLE_WIDTH)


def formatted_time(isotime, localeString="%A, %B %d, %Y at %I:%M%P %Z"):
    dt = dateutil.parser.parse(isotime)
    return dt.strftime(localeString)


def response_check(data, requested):
    if 'message' in data:
        if data['message'] == 'Not Found':
            putln(red, '`{}` not found!'.format(requested))
            clear()
            
        else:
            putln(red, 'Error: {}'.format(data['message']))
            clear()
            
        return False
    return True 


def expand_range(rangeString):
    s, e = [int(i) for i in rangeString.split('-')]
    return list(range(s, e + 1))


def parse_pages(pagesString):
    assert pagesString[0] == 'p'
    pagesString = pagesString[1:]
    each = pagesString.split(',')
    pages = []
    for i in each:
        if '-' in i:
            pages.extend(expand_range(i))
        else:
            pages.append(int(i))
    return pages
