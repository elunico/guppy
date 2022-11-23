from utils import *
from colors import *
import requests
import argparse
from display import *
from issue_display import *
from commit_display import *
from branch_display import *
from caching import *
import dateutil.parser


def parse_repo_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('repo',
                        help='The repo to get information on. Must be in the form of USER/REPO')
    parser.add_argument('-i', '--issues', default=False,
                        help='List all issues on the repo using `all` or a specific issue using `-i NUMBER` or a specific page of issues using -i pNUMBER or -i pFROM-THROUGH or -i pPAGENO,PAGENO2,PAGENO3 or any combination of those. Pages will be returned in the order given and will NOT be sorted (Note all will not display more than 20 pages of issues)')
    parser.add_argument('-b', '--branches', default=False,
                        help='List all branches on the repo using `all` or a specific branch using `-b NUMBER` or a specific page of branches using -b pNUMBER or -b pFROM-THROUGH or -b pPAGENO,PAGENO2,PAGENO3 or any combination of those. Pages will be returned in the order given and will NOT be sorted (Note all will not display more than 20 pages of branches)')
    parser.add_argument('-c', '--commits', default=False,
                        help='List all commits on the repo using `all` or a specific commit using `-c HASH`')
    return parser.parse_args(args)


def fetch_repo_info(user, repo, url, caching=CACHING_ACTIVE):
    """
    Retrieves the general information for a partiular repo either
    from the cache if it exists there for by making a request to
    GitHub if it does not
    """
    if not caching:
        req = requests.get(url.format(user=user, repo=repo))
        repo_info = req.json()
        rate_limit_check(req)
        return repo_info
    else:
        try:
            cached = get_cached_repo("{}/{}".format(user, repo))
        except (IOError, OSError) as e:
            perror("Could not query cache for data: {}".format(e))
            cached = None

        if not cached:
            debug('repo cache miss', yellow)
            clear()
            req = requests.get(url.format(user=user, repo=repo))
            repo_info = req.json()
            rate_limit_check(req)
            cache_repo("{}/{}".format(user, repo), repo_info)
            return repo_info
        else:
            debug('repo cache hit', green)
            clear()
            return cached


def fetch_repo_language(user, repo, url, caching=CACHING_ACTIVE):
    """
    Retrieves the language data for a partiular repo either from the cache if it
    exists there for by making a request to GitHub if it does not
    """
    if not caching:
        req = requests.get(url.format(user=user, repo=repo))
        lang_info = req.json()
        rate_limit_check(req)
        return lang_info
    else:
        cached = get_cached_language("{}/{}".format(user, repo))
        if not cached:
            debug('repo language cache miss', yellow)
            clear()
            req = requests.get(url.format(user=user, repo=repo))
            lang_info = req.json()
            rate_limit_check(req)
            cache_language("{}/{}".format(user, repo), lang_info)
            return lang_info
        else:
            debug('repo language cache hit', green)
            clear()
            return cached


def info_repo(*clas):
    options = parse_repo_args(clas)
    user, repo = options.repo.split('/')

    try:
        repo_info = fetch_repo_info(user, repo, repo_url)
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        perror("Could not retrieve data from internet {}".format(e))
        return 41

    if 'message' in repo_info:
        if repo_info['message'] == 'Not Found':
            putln(red, 'Repo `{}` for user `{}` not found!'.format(repo, user))
            clear()
            return 0
        else:
            putln(red, 'Error: {}'.format(repo_info['message']))
            clear()
            return 0

    # creates the correct DisplayObjects based on the options passed in by the user
    if options.issues is False and options.commits is False and options.branches is False:
        program_name()
        RepoInfoDisplayObject(repo_info).display()
        RepoExtraInfoDisplayObject(repo_info).display()
        RepoLanguageInfoDisplayObject(repo_info).display()
    elif options.issues:
        program_name()
        RepoInfoDisplayObject(repo_info).display()
        nl()
        o = IssueDisplayObjectFactory.forIssue('{}/{}'.format(user, repo),
                                               options.issues,
                                               repo_info['issues_url'][:-9]).display()
    elif options.commits:
        program_name()
        RepoInfoDisplayObject(repo_info).display()
        nl()
        o = CommitDisplayFactory.forCommit('{}/{}'.format(user, repo),
                                           options.commits, repo_info['commits_url'][:-6]).display()
    elif options.branches:
        program_name()
        RepoInfoDisplayObject(repo_info).display()
        nl()
        BranchDisplayFactory.forBranch(
            '{}/{}'.format(user, repo), options.branches, repo_info['branches_url'][:-9]).display()
    else:
        perror("No such option: {}".format(options))
        return 49

    return 0


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

        # displaying title is delegated to injected class
        # to allow for the reuse of this object in multiple
        # contexts. See display.py for more
        self.titler.show_title(self.get_title())

        maxlen = len('Default Branch') + 1

        # puts(bold, "Name: ".ljust(maxlen))
        # puts(black, name)
        putEntry('Name', name, keypad=maxlen)
        # nl()
        # puts(bold, "Link: ".ljust(maxlen))
        # puts(blue + uline, find_at)
        putEntry('Link', find_at, keypad=maxlen, valueColor=blue + uline)
        clear()
        # nl()
        putEntry('Default Branch', self.repo_info['default_branch'], keypad=maxlen)
        clear()
        if self.repo_info['private']:
            putEntry('Visibility', 'private', valueColor=red, keypad=maxlen)
        else:
            putEntry('Visibility', 'public', valueColor=green, keypad=maxlen)
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
        # calculating totals so a percentage can be found
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
        maxlen = 14
        repo_info = self.data
        desc = repo_info['description']
        updated = formatted_time(repo_info['updated_at'])
        putEntry('Last Updated', updated, valueColor=green, keypad=maxlen)
        clear()

        license = repo_info['license']
        if license and license != 'null':
            spdxid = license['spdx_id']
            putEntry('License', license['name'] + " ({})".format(spdxid), valueColor=color_for_license(license),  keypad=maxlen)
            clear()
            nl()
        open_issues_count = repo_info['open_issues']

        putEntry('Open Issues', commify(open_issues_count), keypad=maxlen)
        putEntry('Forks', commify(repo_info['forks']), keypad=maxlen)
        putEntry('Watchers', commify(repo_info['watchers']), keypad=maxlen)
        nl()
        clear()
        putln(bold+uline, "Description")
        clear()
        if not desc:
            putln(magenta, 'No description.')
        else:
            LongTextDisplayObject(desc, CONSOLE_WIDTH - 2, 2).display(magenta)
        clear()
