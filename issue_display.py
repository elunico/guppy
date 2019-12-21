from colors import *
import requests
from utils import *
from repo_display import *
from display import *
from caching import *


def fetch_issue(repo, issue, issues_url, caching=CACHING_ACTIVE):
    """
    Retrieves an issue for a partiular repo either from the cache if it
    exists there for by making a request to GitHub if it does not
    """
    if not caching:
        data = requests.get(issues_url + "/{}".format(issue)).json()
        if not response_check(data):
            return {}
        return data
    else:
        cached = get_cached_issue(repo, issue)
        if not cached:
            debug('cache miss issue', yellow)
            data = requests.get(issues_url + "/{}".format(issue)).json()
            if not response_check(data):
                return {}
            cache_issue(repo, issue, data)
            return data
        else:
            debug('Cache hit issue', green)
            return cached


class IssueDisplayObjectFactory:
    @staticmethod
    def forIssue(repo, issues, issue_url):
        if issues == 'all':
            all_issues = []
            all_issues_pages = get_all_pages_warned(repo, issue_url, 'issues')
            for v in all_issues_pages.values():
                all_issues.extend(v)
            if not all_issues:
                return NoIssueDisplayObject()
            return MultipleIssueDisplayObject(all_issues)
        else:
            if 'p' in issues:
                pages = parse_pages(issues)
                all_issues = []
                all_issues_pages = get_all_data_pages(
                    repo, pages, issue_url, 'issues')
                for v in all_issues_pages.values():
                    all_issues.extend(v)
                if not all_issues:
                    return NoIssueDisplayObject()
                return MultipleIssueDisplayObject(all_issues)
            else:
                issue_info = fetch_issue(repo, issues, issue_url)
                if not issue_info:
                    return NoIssueDisplayObject()
                return SingleLongIssueDisplayObject(issue_info)


class NoIssueDisplayObject(DisplayObject):
    def __init__(self):
        super().__init__({})

    def display(self):
        putln(bold, 'No issues.')


class MultipleIssueDisplayObject(DisplayObject):
    def __init__(self, data):
        super().__init__(data)

    def display(self):
        puts(bold + uline, "Issues in Repo:")
        clear()
        nl()
        for issue in self.data:
            SingleIssueDisplayObject(issue).display()
            putln(black, '=' * CONSOLE_WIDTH)
            nl()


class SingleLongIssueDisplayObject(DisplayObject):
    def __init__(self, issue_data):
        super().__init__(issue_data)

    def display(self):
        SingleIssueDisplayObject(self.data).display()
        puts('  ')
        putln(uline + bold, 'Body:')
        clear()
        body = self.data['body']
        LongTextDisplayObject(body, CONSOLE_WIDTH - 4, 4).display(magenta)
        clear()
        nl()


class SingleIssueDisplayObject(DisplayObject):
    def __init__(self, issue_data):
        super().__init__(issue_data)

    def display(self):
        issue = self.data
        title = issue['title']
        number = issue['number']
        state = issue['state']
        comments = issue['comments']
        created = formatted_time(issue['created_at'])
        updated = formatted_time(issue['updated_at'])
        puts(bold, "  #{}: ".format(number))
        puts(bold, title)
        clear()
        nl()
        puts(red if state == 'closed' else green, "  [{}]".format(state))
        clear()
        nl()
        puts(bold, '  Created: ')
        putln(yellow, created)
        clear()
        puts(bold, '  Updated: ')
        putln(green, updated)
        clear()
        nl()
