from utils import *
from colors import *
import requests
import argparse
from display import *
from issue_display import *
from commit_display import *
import dateutil.parser


class RepoInfoDisplayObject(DisplayObject):
    def __init__(self, repo_info):
        super().__init__(repo_info)
        self.repo_info = repo_info

    def display(self):
        name = self.repo_info['name']
        source = self.repo_info['full_name']
        find_at = self.repo_info['html_url']
        desc = self.repo_info['description']

        title()
        boxed(source)
        nl()
        puts(bold, "Name: ")
        puts(black, name)
        nl()
        puts(bold, "Link: ")
        puts(blue + uline, find_at)
        clear()
        nl()


class RepoLanguageInfoDisplayObject(DisplayObject):
    def __init__(self, repo_info):
        super().__init__(repo_info)
        self.repo_info = repo_info

    def display(self):
        langs = requests.get(self.repo_info['languages_url']).json()
        total = sum([lines for (lang, lines) in langs.items()])
        try:
            longest_lang = max([len(lang) for (lang, lines) in langs.items()])
        except ValueError:
            longest_lang = 2
        langs = {k: ((v / total) * 100) for (k, v) in langs.items()}
        clear()
        nl()
        putln(bold + uline, 'Languages in Repo:')
        clear()
        for (k, v) in langs.items():
            puts(bold, ("  {:>%d}: " % longest_lang).format(k))
            puts(black, "{:.1f}%".format(v))
            nl()


class RepoExtraInfoDisplayObject(DisplayObject):
    def __init__(self, repo_info: dict):
        super().__init__(repo_info)
        self.repo_info = repo_info

    def display(self):
        repo_info = self.data
        desc = repo_info['description']
        updated = formatted_time(repo_info['updated_at'])
        clear()
        nl()
        license = repo_info['license']
        if license and license != 'null':
            puts(bold, 'License: ')
            puts(color_for_license(license), license['name'])
            spdxid = license['spdx_id']
            puts(color_for_license(license), " ({})".format(spdxid))
            clear()
            nl()
        puts(bold, 'Last Updated: ')
        putln(green, updated)
        clear()
        putln(bold, "Description:")
        if not desc:
            putln(magenta, 'No description.')
        else:
            LongTextDisplayObject(desc, CONSOLE_WIDTH - 2, 2).display(magenta)
        clear()


def parse_repo_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'repo', help='The repo to get information on. Must be in the form of USER/REPO')
    parser.add_argument('-i', '--issues', default=False,
                        help='List all issues on the repo using `all` or a specific issue using `-i NUMBER`')
    parser.add_argument('-c', '--commits', default=False,
                        help='List all commits on the repo using `all` or a specific commit using `-c HASH`')
    return parser.parse_args(args)


def info_repo(*clas):
    options = parse_repo_args(clas)
    user, repo = options.repo.split('/')
    req = requests.get(repo_url.format(user=user, repo=repo))
    repo_info = req.json()
    if 'message' in repo_info:
        if repo_info['message'] == 'Not Found':
            putln(red, 'Repo `{}` for user `{}` not found!'.format(repo, user))
            clear()
            return
        else:
            putln(red, 'Error: {}'.format(repo_info['message']))
            clear()
            return

    if options.issues is False and options.commits is False:
        RepoInfoDisplayObject(repo_info).display()
        RepoExtraInfoDisplayObject(repo_info).display()
        RepoLanguageInfoDisplayObject(repo_info).display()
    elif options.issues:
        RepoInfoDisplayObject(repo_info).display()
        nl()
        o = IssueDisplayObjectFactory.forIssue(
            options.issues, repo_info['issues_url'][:-9]).display()
    elif options.commits:
        RepoInfoDisplayObject(repo_info).display()
        nl()
        o = CommitDisplayFactory.forCommit(
            options.commits, repo_info['commits_url'][:-6]).display()
