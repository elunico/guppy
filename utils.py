import sys
import re
import requests
import os
import dateutil.parser
from colors import *
from caching import get_cached_user_list, get_cached_repo_list, cache_user_list, cache_repo_list, CACHING_ACTIVE


MAX_PAGES = 5

user_url = 'https://api.github.com/users/{user}'
usr_repos_url = 'https://api.github.com/users/{user}/{repo}'
repo_url = 'https://api.github.com/repos/{user}/{repo}'
languages_url = 'https://api.github.com/repos/{user}/{repo}/languages'

usage = "Usage: {0} mode. Try '{0} help' for help".format(sys.argv[0])


def formatted_time(isotime, localeString="%A, %B %d, %Y at %I:%M%P %Z"):
    """
    Return an ISO time string formatted for locale
    """
    dt = dateutil.parser.parse(isotime)
    return dt.strftime(localeString)


def response_check(data, requested='resource'):
    """
    Check the status of the JSON returned by a GitHub reponse.
    Prints an error if an error occurs and returns False
    otherwise returns True
    """
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
    """
    Turns page ranges into lists of pages.
    E.g. turns 3-6 into [3, 4, 5, 6]
    """
    s, e = [int(i) for i in rangeString.split('-')]
    return list(range(s, e + 1))


def parse_pages(pagesString):
    """
    Turn a pages string into a list of pages
    Turns 'p3,4,6-9' into [3,4,5,6,7,8,9].
    The string MUST be prefixed with 'p'
    """
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


def get_max_pages(url):  # -> List[int]
    """
    Fetches data from `url` and uses the `Link` header,
    if present, to find how many pages are needed to
    retrieve all the data.

    Returns two values

    First it returns if there are more pages needed for the
    resource than allowed by MAX_PAGES

    Second It will return all pages until the number of
    pages is equal to MAX_PAGES. It will not return a list of
    pages that surpases MAX_PAGES. This list is a list of numbers
    indicating which pages should be queried
    """
    issue_req = requests.get(url)
    if 'Link' not in issue_req.headers:
        debug('Link header not found', yellow)
        return False, [1]
    if not response_check(issue_req):
        return False, []
    last_page = max((int(i) for i in re.findall(
        r'\?page=(\d+)', issue_req.headers.get('Link', ''))), default=0)

    return last_page > MAX_PAGES, list(range(1, last_page + 1))


def fetch_data_page(source, page, base_url, list, caching=CACHING_ACTIVE):
    """
    A cache aware function that either gets a particular page from the cache
    or requests from GitHub that page of data.
    Works with user info: followers, following, gists, repos and
    repo info: commits, issues, branches, contributors.

    source is the source either the username or repo (needed for cache retrieval)
    page is the page (e.g. 1 or 2 or 4 etc.) to retrieve
    base_url is the url of the resource to which "?page=X" is attached
    list is the a string that indicates the kind of data that is retrieved any of 'following', 'followers', 'gists', 'repos', 'commits', or 'issues'
    caching indicates whether to use caching
    """
    if not caching:
        req = requests.get(base_url + "?page={}".format(page))
        if not response_check(req):
            return []
        info = req.json()
        if not info:
            return []
        return info
    else:
        if list in ['followers', 'following', 'gists', 'repos']:
            cached = get_cached_user_list(source,  list, page)
        elif list in ['commits', 'issues', 'branches', 'contributors']:
            cached = get_cached_repo_list(source, list, page)
        else:
            raise AssertionError(
                'Value {} was unexpected for argument list in fetch_data_page'.format(list))
        if cached:
            debug('cache hit fetch data page', green)
            return cached
        else:
            debug('cache miss fetch data page', yellow)
            req = requests.get(base_url + "?page={}".format(page))
            if not response_check(req):
                return []
            info = req.json()
            if not info:
                return []
            if list in ['followers', 'following', 'gists', 'repos']:
                cache_user_list(source, list, page, info)
            elif list in ['commits', 'issues', 'branches', 'contributors']:
                cache_repo_list(source, list, page, info)
            return info


def get_all_data_pages(source, pages_list, base_url, list):
    """
    Retrieves all the pages_list pages of `list` kind of data (followers,
    following, gists, repos, commits, issues, branches, contributors)
    either from the cache if present or by making a request to
    base_url for the user or repo specified by source
    """
    all_data = {}
    for page in pages_list:
        info = fetch_data_page(source, page, base_url, list)
        if not info:
            return {}
        all_data[page] = info
    return all_data


def get_all_pages_warned(source, base_url, list_):
    """
    Determines the number of pages required to send back the
    type of resource specified by list_ (followers,
    following, gists, repos, commits, issues, branches, or contributors)
    and prints a warning if it takes more than MAX_PAGES
    pages to do so. Source is the user or repo from which
    the `list_` data is coming. Data is either retrieved from
    cache or by requesting base_url
    """
    (overflow, pages_list) = get_max_pages(base_url)
    if overflow:
        putln(yellow, "Warning: only first {} pages of {} total pages of "
              "of data will be shown. Use -i pNUMBER to "
              "see other pages".format(MAX_PAGES, pages_list[-1]))
        pages_list = list(range(1, MAX_PAGES + 1))
    all_issues = get_all_data_pages(source, pages_list, base_url, list_)
    return all_issues


def rate_limit_check(req):
    """
    Checks the headers of a requests response object
    and prints a warning if rate limiting will soon take affect
    """
    if 'X-RateLimit-Remaining' in req.headers:
        left = int(req.headers['X-RateLimit-Remaining'])
        if left < 20:
            putln(yellow + bold, 'Rate Limit Warning! {} requests left. Appox. {} - {} invocations remaining'.format(
                left, int(left / 6), int(left / 2)))
            clear()
