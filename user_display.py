import argparse
import requests
from utils import *
from colors import *
from display import *
from gists_display import *
from repo_display import RepoInfoDisplayObject
from follow_display import *
from caching import *


def parse_repo_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'user', help='The user to get information on.')
    parser.add_argument('-r', '--repos', default=False,
                        help='List all repos for the user. List pages using -r p2,3,4-7 etc. syntax. To list a specific repo, use the `repo` action instead of `user` action')
    parser.add_argument('-g', '--gists', default=False,
                        help='List all gists for the user using `all` or a specific gist using `-g GIST_ID`. Can also use page syntax as in -r')
    parser.add_argument('--followers', default=False,
                        help='List all followers for the user. Can also use page syntax as in -r. To see a specific follower use the `user` option and their handle')
    parser.add_argument('--following', default=False,
                        help='List all following for the user. Can also use page syntax as in -r. To see a specific following use the `user` option and their handle')
    return parser.parse_args(args)


def fetch_user_info(username, url, caching=CACHING_ACTIVE):
    if not caching:
        req = requests.get(url.format(user=username))
        user_info = req.json()
        rate_limit_check(req)
        return user_info
    else:
        try:
            cached = get_cached_user(username)
        except (IOError, OSError) as e:
            perror('Could not retrieve cache values. Request will be made')
            cached = None

        if not cached:
            debug('cache miss', yellow)
            clear()
            req = requests.get(url.format(user=username))
            user_info = req.json()
            rate_limit_check(req)
            cache_user(username, user_info)
            return user_info
        else:
            debug('cache hit', green)
            clear()
            return cached


def info_user(*clas):
    options = parse_repo_args(clas)
    user = options.user
    try:
        user_info = fetch_user_info(user, user_url)
        if not response_check(user_info, user):
            return
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        perror("Could not fetch user data from internet {}".format(e))
        return 31

    # creates the correct DisplayObjects based on the options passed in by the user
    # Use of factories and polymorphismhelps to abstract away the choices
    #  around -X all, -X pPAGE, etc.
    if options.repos is False and options.gists is False and options.followers is False and options.following is False:
        program_name()
        UserInfoDisplayObject(user_info).display()
        nl()
        UserExtraInfoDisplayObject(user_info).display()
        return 0
    elif options.repos:
        repos = UserReposDisplayObjectFactory.forRepos(user, options.repos, user_info['repos_url'])
        if repos is None:
            return 1
        program_name()
        UserInfoDisplayObject(user_info).display()
        nl()
        repos.display()
        return 0
    elif options.gists:
        program_name()
        UserInfoDisplayObject(user_info).display()
        nl()
        UserGistsDisplayObjectFactory.forGists(user,
                                               options.gists, user_info['gists_url'][:-10]).display()
        return 0
    elif options.following:
        program_name()
        UserInfoDisplayObject(user_info).display()
        nl()
        UserFollowDisplayObjectFactory.forFollow(
            user, 'following', options.following, user_info['following_url'][:-13]).display()
        return 0
    elif options.followers:
        program_name()
        UserInfoDisplayObject(user_info).display()
        nl()
        UserFollowDisplayObjectFactory.forFollow(
            user, 'followers', options.followers, user_info['followers_url']).display()
        return 0
    else:
        perror('No such option: {}'.format(options))
        return 39


class NoReposDisplayObject(DisplayObject):
    def __init__(self):
        super().__init__({})

    def display(self):
        print(bold, "No repo found.")


class UserReposDisplayObjectFactory:
    @staticmethod
    def forRepos(user, repos, repos_url):
        if repos == 'all':
            debug('all')
            all_repos = []
            all_repos_pages = get_all_pages_warned(user, repos_url, 'repos')
            for v in all_repos_pages.values():
                all_repos.extend(v)
            if not all_repos:
                return NoReposDisplayObject()
            return UserMultipleReposDisplayObject(all_repos)
        else:
            if 'p' in repos:
                pages = parse_pages(repos)
                all_repos = []
                all_repos_pages = get_all_data_pages(
                    user, pages, repos_url, 'repos')
                for v in all_repos_pages.values():
                    all_repos.extend(v)
                if not all_repos:
                    return NoReposDisplayObject()
                return UserMultipleReposDisplayObject(all_repos)
            else:
                perror(
                    'Examine a specific repo using the REPO option! Try python3 guppy.py HELP for more.')
                return None


class UserInfoDisplayObject(DisplayObject):
    def __init__(self, user_data, titler=BoxedTitleDisplayer()):
        super().__init__(user_data)
        self.titler = titler

    def display(self):
        self.titler.show_title("{} (@{})".format(
            self.data['name'], self.data['login']))
        putEntry('URL', self.data['html_url'], valueColor=blue)


class UserExtraInfoDisplayObject(DisplayObject):
    def __init__(self, user_data):
        super().__init__(user_data)

    def display(self):
        bio = self.data['bio']
        if bio:
            putln(bold + uline, 'About:')
            clear()
            LongTextDisplayObject(
                bio, CONSOLE_WIDTH - 2, 2).display(magenta)
            nl()
        if self.data['blog']:
            putEntry('Website',
                     self.data['blog'], valueColor=blue)
            nl()
        putEntry('Number of (public) repos',
                 commify(self.data['public_repos']))
        putEntry('Number of (public) gists',
                 commify(self.data['public_gists']))
        nl()
        putEntry('Followers', commify(self.data['followers']))
        putEntry('Following', commify(self.data['following']))


class UserMultipleReposDisplayObject(DisplayObject):
    def __init__(self, repos_data):
        super().__init__(repos_data)

    def display(self):
        for repo_data in self.data:
            RepoInfoDisplayObject(repo_data, PlainTitleDisplayer()).display()
            putln('=' * CONSOLE_WIDTH)
            nl()


class UserGistsDisplayObject(DisplayObject):
    def __init__(self, gists_data):
        super().__init__(gists_data)

    def display(self):
        for repo_data in self.data:
            RepoInfoDisplayObject(repo_data, PlainTitleDisplayer()).display()
            putln('=' * CONSOLE_WIDTH)
            nl()
