from colors import *
import textwrap
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
            return SingleIssueDisplayObject(issue_info)


class NoIssueDisplayObject(DisplayObject):
    def __init__(self):
        super().__init__({})

    def display(self):
        putln(bold, 'No issues.')


class MultipleIssueDisplayObject(DisplayObject):
    def __init__(self, data):
        super().__init__(data)

    def display(self):
        print(self.data)
        for issue in self.data:
            SingleIssueDisplayObject(issue).display()


class SingleIssueDisplayObject(DisplayObject):
    def __init__(self, issue_data):
        super().__init__(issue_data)

    def display(self):
        issue = self.data
        title = issue['title']
        number = issue['number']
        state = issue['state']
        comments = issue['comments']
        body = issue['body']
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
        puts('  ')
        putln(uline + bold, 'Body:')
        clear()
        puts(black, textwrap.indent('\n'.join(textwrap.wrap(body)), '    '))
        clear()
        nl()
        putln(black, '=' * CONSOLE_WIDTH)
        nl()
