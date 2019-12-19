import os
import subprocess
import sys
import re
import requests
import dateutil.parser
from colors import *


MAX_PAGES = 5

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


def response_check(data, requested='resource'):
    if 'message' in data:
        if data['message'] == 'Not Found':
            putln(red, 'Error: {} not found!'.format(requested))
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


def get_max_pages(url):
    issue_req = requests.get(url)
    assert('Link' in issue_req.headers)
    if not response_check(issue_req):
        return False, []
    last_page = max((int(i) for i in re.findall(
        r'\?page=(\d+)', issue_req.headers.get('Link', ''))), default=0)

    return last_page > MAX_PAGES, list(range(1, last_page + 1))


def get_all_data_pages(pages_list, base_url):
    all_issues = {}
    for page in pages_list:
        issue_req = requests.get(
            base_url + "?page={}".format(page))
        if not response_check(issue_req):
            return {}
        issue_info = issue_req.json()
        if not issue_info:
            return {}
        all_issues[page] = issue_info
    return all_issues


def get_all_pages_warned(base_url):
    (overflow, pages_list) = get_max_pages(base_url)
    if overflow:
        putln(yellow, "Warning: only first {} pages of {} total pages of "
              "of data will be shown. Use -i pNUMBER to "
              "see other pages".format(MAX_PAGES, pages_list[-1]))
        pages_list = list(range(1, MAX_PAGES + 1))
    all_issues = get_all_data_pages(pages_list, base_url)
    return all_issues


def rate_limit_check(req):
    if 'X-RateLimit-Remaining' in req.headers:
        left = int(req.headers['X-RateLimit-Remaining'])
        if left < 20:
            putln(yellow + bold, 'Rate Limit Warning! {} requests left. Appox. {} - {} invocations remaining'.format(
                left, int(left / 6), int(left / 2)))
            clear()


if os.environ.get('DEBUG', False):

    import inspect

    def line():
        return inspect.getframeinfo(inspect.currentframe()).lineno

    def debug(msg, color=black):
        print("{3}DEBUG: [{0}:{1}] {2}{4}".format(
            __name__, line(), msg, color, black))
else:
    def line(): return ''

    def debug(*args, **kwargs): pass
