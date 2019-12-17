from colors import *
import requests
from utils import *
from repo_display import *
from display import *
import re

MAX_ISSUE_PAGES = 5


def get_max_issue_pages(url):
    issue_req = requests.get(url)
    last_page = max((int(i) for i in re.findall(
        r'\?page=(\d+)', issue_req.headers.get('Link', ''))), default=0)

    return last_page > MAX_ISSUE_PAGES, list(range(1, last_page + 1))


def get_all_issue_data_pages(pages_list, issue_url):
    all_issues = []
    for page in pages_list:
        issue_req = requests.get(
            issue_url + "?page={}".format(page))
        issue_info = issue_req.json()
        if not issue_info:
            return []
        all_issues.extend(issue_info)
    return all_issues


class IssueDisplayObjectFactory:
    @staticmethod
    def forIssue(issues, issue_url):
        if issues == 'all':
            (overflow, pages_list) = get_max_issue_pages(issue_url)
            if overflow:
                putln(
                    yellow, "Warning: only first {} pages of {} total pages of issues will be shown. Use -i pNUMBER to see other pages".format(MAX_ISSUE_PAGES, pages_list[-1]))
                pages_list = list(range(1, MAX_ISSUE_PAGES + 1))
            all_issues = get_all_issue_data_pages(pages_list, issue_url)
            if not all_issues:
                return NoIssueDisplayObject()
            return MultipleIssueDisplayObject(all_issues)
        else:
            if 'p' in issues:
                pages = parse_pages(issues)
                all_issues = get_all_issue_data_pages(pages, issue_url)
                if not all_issues:
                    return NoIssueDisplayObject()
                return MultipleIssueDisplayObject(all_issues)
            else:
                issue_info = requests.get(
                    issue_url + "/{}".format(issues)).json()
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
