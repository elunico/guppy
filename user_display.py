import argparse
import requests
from utils import *
from colors import *
from display import *
from repo_display import RepoInfoDisplayObject


def parse_repo_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'user', help='The user to get information on.')
    parser.add_argument('-r', '--repos', default=False, action='store_true',
                        help='List all repos for the user. To list a specific repo, use the `repo` action instead of `user` action')
    parser.add_argument('-g', '--gists', default=False,
                        help='List all gists for the user using `all` or a specific commit using `-g GIST`')
    parser.add_argument('--followers', default=False, action='store_true',
                        help='List all followers for the user. To see a specific follower use the `user` option and their handle')
    parser.add_argument('--following', default=False, action='store_true',
                        help='List all following for the user. To see a specific following use the `user` option and their handle')
    return parser.parse_args(args)


def info_user(*clas):
    options = parse_repo_args(clas)
    user = options.user
    req = requests.get(user_url.format(user=user))
    user_info = req.json()
    if not response_check(user_info, user):
        return

    if options.repos is False and options.gists is False and options.followers is False and options.following is False:
        program_name()
        UserInfoDisplayObject(user_info).display()
        nl()
        UserExtraInfoDisplayObject(user_info).display()
    elif options.repos:
        program_name()
        UserInfoDisplayObject(user_info).display()
        nl()
        data = requests.get(user_info['repos_url']).json()
        if not response_check(data, 'repos'):
            return
        o = UserReposDisplayObject(data).display()
    elif options.gists:
        program_name()
        UserInfoDisplayObject(user_info).display()
        nl()
        data = requests.get(user_info['gists_url'][:-10]).json()
        if not response_check(data, 'gists'):
            return
        print(data)
        o = UserReposDisplayObject(data).display()
    elif options.following:
        pass
    elif options.followers:
        pass


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


class UserReposDisplayObject(DisplayObject):
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
