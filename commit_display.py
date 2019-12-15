from colors import *
from utils import *
import requests
from repo_display import *
from display import *


class CommitDisplayFactory:

    @staticmethod
    def forCommit(commit, commits_url):
        if commit == 'all':
            commit_info = requests.get(commits_url).json()
            if not commit_info:
                return NoCommitDisplayObject()
            return MultipleCommitDisplayObject(commit_info)
        else:
            commit_info = requests.get(
                "{}/{}".format(commits_url, commit)).json()
            if not commit_info:
                return NoCommitDisplayObject()
            return SingleLongCommitDisplayObject(commit_info)


class NoCommitDisplayObject(DisplayObject):
    def __init__(self):
        super().__init__({})

    def display(self):
        print(bold, "No commits.")


class SingleLongCommitDisplayObject(DisplayObject):
    def __init__(self, issue_data):
        super().__init__(issue_data)

    def display(self):
        SingleCommitDisplayObject(self.data).display()
        nl()
        putln(bold, '  Message: ')
        clear()
        message = self.data['commit']['message']
        LongTextDisplayObject(message, CONSOLE_WIDTH - 4, 4).display(magenta)
        clear()
        putln(black, '=' * CONSOLE_WIDTH)
        nl()


class SingleCommitDisplayObject(DisplayObject):
    def __init__(self, commit_data):
        super().__init__(commit_data)

    def display(self):
        commit = self.data
        sha = commit['sha']
        commit_author = commit['commit']['author']['name']
        commit_author_email = commit['commit']['author']['email']
        commit_author_date = commit['commit']['author']['date']
        commit_committer = commit['commit']['committer']['name']
        commit_committer_email = commit['commit']['committer']['email']
        commit_committer_date = commit['commit']['committer']['date']
        url = commit['html_url']
        puts(bold + uline, 'Commit: {}'.format(sha))
        clear()
        nl()
        nl()
        putln(bold, '  Author:')
        putln(black, '    {} ({}) at {}'.format(
            commit_author, commit_author_email, commit_author_date))
        clear()
        nl()
        putln(bold, '  Committer: ')
        putln(black, '    {} ({}) at {}'.format(
            commit_committer, commit_committer_email, commit_committer_date))
        clear()
        nl()
        puts(bold, '  URL: ')
        putln(green + uline, url)
        clear()


class MultipleCommitDisplayObject(DisplayObject):
    def __init__(self, data):
        super().__init__(data)

    def display(self):
        puts(bold + uline, "Commits in Repo:")
        clear()
        nl()
        for commit in self.data:
            SingleCommitDisplayObject(commit).display()
            putln(black, '=' * CONSOLE_WIDTH)
            nl()
            clear()
