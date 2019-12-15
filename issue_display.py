from colors import *
import requests
from utils import *
from repo_display import *
from display import *


class IssueDisplayObjectFactory:
    @staticmethod
    def forIssue(issues, issue_url):
        if issues == 'all':
            issue_info = requests.get(issue_url).json()
            if not issue_info:
                return NoIssueDisplayObject()
            return MultipleIssueDisplayObject(issue_info)
        else:
            issue_info = requests.get(issue_url + "/{}".format(issues)).json()
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
