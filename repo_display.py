from utils import *
from colors import *
import requests
import textwrap
import argparse
from display import *
from issue_display import *
from commit_display import *


class RepoInfoDisplayObject(DisplayObject):
    def __init__(self, repo_info):
        super().__init__(repo_info)
        self.repo_info = repo_info

    def display(self):
        name = self.repo_info['name']
        source = self.repo_info['full_name']
        find_at = self.repo_info['html_url']
        desc = self.repo_info['description']

        print("~*~*~*~* G I T H U B    C O N S O L E *~*~*~*~".center(CONSOLE_WIDTH))
        boxed(name)
        nl()
        puts(bold, "Under: ")
        puts(black, source)
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
        longest_lang = max([len(lang) for (lang, lines) in langs.items()])
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
        putln(bold, "Description:")
        putln(
            magenta,
            textwrap.indent(
                '\n'.join(textwrap.wrap(desc, width=CONSOLE_WIDTH - 2)), '  '
            )
        )
        clear()


def parse_repo_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'repo', help='The repo to get information on. Must be in the form of USER/REPO')
    parser.add_argument('-i', '--issues', default=False,
                        help='List all issues on the repo using `all` or a specific issue using `-i NUMBER`')
    parser.add_argument('-c', '--commits', default=False,
                        help='List all commits on the repo using `all` or a specific commit using `-i SHA`')
    return parser.parse_args(args)


def info_repo(*clas):
    # todo: use argparse to parse remaining args by passing list?
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
        puts(bold + uline, "Issues in Repo:")
        clear()
        nl()
        o = IssueDisplayObjectFactory.forIssue(
            options.issues, repo_info['issues_url'][:-9]).display()
    elif options.commits:
        RepoInfoDisplayObject(repo_info).display()
        nl()
        puts(bold + uline, "Commits in Repo:")
        clear()
        nl()
        o = CommitDisplayFactory.forCommit(
            options.commits, repo_info['commits_url'][:-6]).display()
