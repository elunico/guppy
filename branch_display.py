import requests
from caching import *
from display import *
from utils import response_check, parse_pages, get_all_data_pages, get_all_pages_warned


def fetch_branch(repo, branch, branch_url, caching=CACHING_ACTIVE):
    if not caching:
        data = requests.get("{}/{}".format(branch_url, branch)).json()
        if not response_check(data):
            return {}
        return data
    else:
        cached = get_cached_branch(repo, branch)
        if not cached:
            debug('cache miss branch', yellow)
            data = requests.get("{}/{}".format(branch_url, branch)).json()
            if not response_check(data):
                return {}
            cache_branch(repo, branch, data)
            return data
        else:
            debug('Cache hit branch', green)
            return cached


class BranchDisplayFactory:

    @staticmethod
    def forBranch(repo, branch, branches_url):
        """
        `branch` is the string passed on the command line specifying
        which branches want to be seen. It is either all, pPAGES, or a branch name
        """
        if branch == 'all':
            all_branches = []
            # get_all_data_pages and get_all_pages_warned are
            # cache aware functions that work similarly to fetch_branch
            all_branches_pages = get_all_pages_warned(
                repo, branches_url, 'branches')
            for v in all_branches_pages.values():
                all_branches.extend(v)
            if not all_branches:
                return NoBranchDisplayObject()
            return MultipleBranchDisplayObject(all_branches)
        else:
            if 'p' in branch:
                pages = parse_pages(branch)
                all_branches = []
                all_branches_pages = get_all_data_pages(
                    repo, pages, branches_url, 'branches')
                for v in all_branches_pages.values():
                    all_branches.extend(v)
                if not all_branches:
                    return NoBranchDisplayObject()
                return MultipleBranchDisplayObject(all_branches)
            else:
                branch_info = fetch_branch(repo, branch, branches_url)
                if not branch_info:
                    return NoBranchDisplayObject()
                return SingleLongBranchDisplayObject(branch_info)


class NoBranchDisplayObject(DisplayObject):
    def __init__(self):
        super().__init__({})

    def display(self):
        putln(red, 'No branches!')
        clear()


class SingleLongBranchDisplayObject(DisplayObject):
    def __init__(self, data):
        super().__init__(data)

    def display(self):
        SingleBranchDisplayObject(self.data).display()
        nl()
        if self.data['protected']:
            putln(bold + uline, 'Required Status Checks')
            clear()
            putEntry('Level', self.data['protection']
                     ['required_status_checks']['enforcement_level'])
            putln(bold, 'Contexts: ')
            clear()
            for item in self.data['protection']['required_status_checks']['contexts']:
                putln(black, '  {}'.format(item))


class SingleBranchDisplayObject(DisplayObject):
    def __init__(self, data):
        super().__init__(data)

    def display(self):
        puts(bold, 'Name: ')
        puts(black, self.data['name'])
        puts(black, '  ')
        if self.data['protected']:
            putln(red, '[protected]')
        clear()

        putEntry('HEAD', self.data['commit']['sha'])


class MultipleBranchDisplayObject(DisplayObject):
    def __init__(self, data):
        super().__init__(data)

    def display(self):
        puts(bold + uline, "Branchs in Repo:")
        clear()
        nl()
        for branch in self.data:
            SingleBranchDisplayObject(branch).display()
            putln(black, '=' * CONSOLE_WIDTH)
            nl()
            clear()
