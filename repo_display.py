from utils import *
from colors import *
import requests
import argparse
from display import *
from issue_display import *
from commit_display import *
from caching import *
import dateutil.parser


def parse_repo_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'repo', help='The repo to get information on. Must be in the form of USER/REPO')
    parser.add_argument('-i', '--issues', default=False,
                        help='List all issues on the repo using `all` or a specific issue using `-i NUMBER` or a specific page of issues using -i pNUMBER or -i pFROM-THROUGH or -i pPAGENO,PAGENO2,PAGENO3 or any combination of those. Pages will be returned in the order given and will NOT be sorted (Note all will not display more than 20 pages of issues)')
    parser.add_argument('-c', '--commits', default=False,
                        help='List all commits on the repo using `all` or a specific commit using `-c HASH`')
    return parser.parse_args(args)


def fetch_repo_info(user, repo, url, caching=CACHING_ACTIVE):
    if not caching:
        req = requests.get(url.format(user=user, repo=repo))
        repo_info = req.json()
        rate_limit_check(req)
        return repo_info
    else:
        cached = get_cached_repo("{};{}".format(user, repo))
        if not cached:
            debug('repo cache miss', yellow)
            clear()
            req = requests.get(url.format(user=user, repo=repo))
            repo_info = req.json()
            rate_limit_check(req)
            cache_repo("{};{}".format(user, repo), repo_info)
            return repo_info
        else:
            debug('repo cache hit', green)
            clear()
            return cached


def fetch_repo_language(user, repo, url, caching=CACHING_ACTIVE):
    if not caching:
        req = requests.get(url.format(user=user, repo=repo))
        lang_info = req.json()
        rate_limit_check(req)
        return lang_info
    else:
        cached = get_cached_language("{};{}".format(user, repo))
        if not cached:
            debug('repo language cache miss', yellow)
            clear()
            req = requests.get(url.format(user=user, repo=repo))
            lang_info = req.json()
            rate_limit_check(req)
            cache_language("{};{}".format(user, repo), lang_info)
            return lang_info
        else:
            debug('repo language cache hit', green)
            clear()
            return cached


def info_repo(*clas):
    options = parse_repo_args(clas)
    user, repo = options.repo.split('/')
    repo_info = fetch_repo_info(user, repo, repo_url)

    # TODO: replace with response_check
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
        program_name()
        RepoInfoDisplayObject(repo_info).display()
        RepoExtraInfoDisplayObject(repo_info).display()
        RepoLanguageInfoDisplayObject(repo_info).display()
    elif options.issues:
        program_name()
        RepoInfoDisplayObject(repo_info).display()
        nl()
        o = IssueDisplayObjectFactory.forIssue(
            options.issues, repo_info['issues_url'][:-9]).display()
    elif options.commits:
        program_name()
        RepoInfoDisplayObject(repo_info).display()
        nl()
        o = CommitDisplayFactory.forCommit(
            options.commits, repo_info['commits_url'][:-6]).display()


class RepoInfoDisplayObject(DisplayObject):
    def __init__(self, repo_info, titler=BoxedTitleDisplayer()):
        super().__init__(repo_info)
        self.repo_info = repo_info
        self.titler = titler

    def get_title(self):
        title = self.repo_info['full_name']
        if self.repo_info['fork'] and 'parent' in self.repo_info and 'full_name' in self.repo_info['parent']:
            origin = self.repo_info['parent']['full_name']
            title += '\n[forked from: {}]'.format(origin)
        elif self.repo_info['fork']:
            title += ' {}[fork]{}'.format(magenta, black)
        return title

    def display(self):
        name = self.repo_info['name']
        find_at = self.repo_info['html_url']
        desc = self.repo_info['description']

        self.titler.show_title(self.get_title())

        puts(bold, "Name: ")
        puts(black, name)
        nl()
        puts(bold, "Link: ")
        puts(blue + uline, find_at)
        nl()
        clear()
        if self.repo_info['private']:
            putEntry('Visibility', 'private', valueColor=red)
        else:
            putEntry('Visibility', 'public', valueColor=green)
        clear()
        nl()


class RepoLanguageInfoDisplayObject(DisplayObject):
    def __init__(self, repo_info):
        super().__init__(repo_info)
        self.repo_info = repo_info

    def display(self):
        user, repo = self.repo_info['full_name'].split('/')
        langs = fetch_repo_language(
            user, repo, self.repo_info['languages_url'])
        if not response_check(langs, 'languages'):
            return
        total = sum([lines for (lang, lines) in langs.items()])
        try:
            longest_lang = max([len(lang) for (lang, lines) in langs.items()])
        except ValueError:
            longest_lang = 2
        lang_percents = {k: ((v / total) * 100) for (k, v) in langs.items()}
        clear()
        nl()
        putln(bold + uline, 'Major Languages in Repo:')
        clear()
        for (k, v) in lang_percents.items():
            if v < 0.1:
                break
            puts(bold, ("  {:>%d}: " % longest_lang).format(k))
            puts(black, "{:2.1f}% ({})".format(v, fmt_bytes(langs[k])))
            nl()
        additional = []
        for (k, v) in lang_percents.items():
            if v < 0.1:
                additional.append(k)
        if additional:
            nl()
            putln(bold + uline, "Additional languages (< 0.1%): ")
            LongTextDisplayObject(', '.join(additional),
                                  CONSOLE_WIDTH - 2, 2).display()


class RepoExtraInfoDisplayObject(DisplayObject):
    def __init__(self, repo_info: dict):
        super().__init__(repo_info)
        self.repo_info = repo_info

    def display(self):
        repo_info = self.data
        desc = repo_info['description']
        updated = formatted_time(repo_info['updated_at'])
        putEntry('Last Updated', updated, valueColor=green)
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
            nl()
        open_issues_count = repo_info['open_issues']

        putEntry('Open Issues', commify(open_issues_count))
        putEntry('Forks', commify(repo_info['forks']))
        putEntry('Watchers', commify(repo_info['watchers']))
        nl()
        clear()
        putln(bold, "Description:")
        if not desc:
            putln(magenta, 'No description.')
        else:
            LongTextDisplayObject(desc, CONSOLE_WIDTH - 2, 2).display(magenta)
        clear()
