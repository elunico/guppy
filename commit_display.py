from caching import get_cached_commit, cache_commit
from colors import *
from utils import *
import requests
from repo_display import *
from display import *
import pprint


def fetch_commit(repo, commit, commits_url, caching=CACHING_ACTIVE):
    """
    Retrieves a commit for a partiular repo either from the cache if it
    exists there for by making a request to GitHub if it does not
    """
    if not caching:
        data = requests.get("{}/{}".format(commits_url, commit)).json()
        if not response_check(data):
            return {}
        return data
    else:
        cached = get_cached_commit(repo, commit)
        if not cached:
            debug('cache miss commit', yellow)
            data = requests.get("{}/{}".format(commits_url, commit)).json()
            if not response_check(data):
                return {}
            cache_commit(repo, commit, data)
            return data
        else:
            debug('Cache hit commit', green)
            return cached


class CommitDisplayFactory:

    @staticmethod
    def forCommit(repo, commit, commits_url):
        """
        `commit` is the string passed on the command line specifying
        which commits want to be seen. It is either all, pPAGES, or a commit SHA
        """
        if commit == 'HEAD':
            data = get_all_data_pages(
                repo, [1], commits_url, 'commits', caching=False)
            if not data:
                return NoCommitDisplayObject()
            # remember get_all_data_pages returns a dict of page number to list of resources (dict)
            commit = data[1][0]
            sha = commit['sha']
            # the data gotten by /commits has less information than /commits/:sha
            # so we need to find the head without using cache then retrieve that
            # commit. Once we are sure which commit is HEAD, we can try to get it
            # from the cache
            info = fetch_commit(repo, sha, commits_url)
            if not info:
                return NoCommitDisplayObject()
            return SingleLongCommitDisplayObject(info)
        if commit == 'all':
            all_commits = []
            # get_all_data_pages and get_all_pages_warned are
            # cache aware functions that work similarly to fetch_commit
            all_commits_pages = get_all_pages_warned(
                repo, commits_url, 'commits')
            for v in all_commits_pages.values():
                all_commits.extend(v)
            if not all_commits:
                return NoCommitDisplayObject()
            return MultipleCommitDisplayObject(all_commits)
        else:
            if 'p' in commit:
                pages = parse_pages(commit)
                all_commits = []
                all_commits_pages = get_all_data_pages(
                    repo, pages, commits_url, 'commits')
                for v in all_commits_pages.values():
                    all_commits.extend(v)
                if not all_commits:
                    return NoCommitDisplayObject()
                return MultipleCommitDisplayObject(all_commits)
            else:
                commit_info = fetch_commit(repo, commit, commits_url)
                if not commit_info:
                    return NoCommitDisplayObject()
                return SingleLongCommitDisplayObject(commit_info)


class NoCommitDisplayObject(DisplayObject):
    def __init__(self):
        super().__init__({})

    def display(self):
        print(bold, "No commits.")


def colorForStatus(status):
    if status == 'modified':
        return yellow
    if status == 'added':
        return green
    if status == 'deleted' or status == 'removed':
        return red
    return 'MISSING COLOR'


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
        nl()
        puts(black, '  ')
        putln(bold + uline, 'Files changed:')
        clear()
        nl()
        for f in self.data['files']:
            puts(black, '    ')
            puts(colorForStatus(f['status']), '[{}] ' .format(f['status']))
            clear()
            puts(bold, f['filename'])
            clear()
            puts(black, ' (')
            puts(green, '+{}'.format(f['additions']))
            puts(black, ', ')
            puts(red, '-{}'.format(f['deletions']))
            puts(black, ', ')
            puts(yellow, '±{}'.format(f['changes']))
            puts(black, ')')
            clear()
            nl()
            clear()
            nl()

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
