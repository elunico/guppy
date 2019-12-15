import argparse
import requests
from utils import *
from colors import *
from display import *


def parse_repo_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'user', help='The user to get information on.')
    parser.add_argument('-r', '--repos', default=False,
                        help='List all repos for the user using `all` or a specific issue using `-r NAME`')
    parser.add_argument('-g', '--gists', default=False,
                        help='List all gists for the user using `all` or a specific commit using `-g GIST`')
    parser.add_argument('--followers', default=False,
                        help='List all followers for the user')
    parser.add_argument('--following', default=False,
                        help='List all following for the user')
    return parser.parse_args(args)


def info_user(*clas):
    options = parse_repo_args(clas)
    user = options.user
    req = requests.get(user_url.format(user=user))
    user_info = req.json()
    if 'message' in user_info:
        if user_info['message'] == 'Not Found':
            putln(red, 'User `{}` not found!'.format(user))
            clear()
            return
        else:
            putln(red, 'Error: {}'.format(user_info['message']))
            clear()
            return

    if options.repos is False and options.gists is False and options.followers is False and options.following is False:
        title()
        UserInfoDisplayObject(user_info).display()
        nl()
        UserExtraInfoDisplayObject(user_info).display()
    elif options.repos:
        pass
        # RepoInfoDisplayObject(user_info).display()
        # nl()
        # o = IssueDisplayObjectFactory.forIssue(
        #     options.issues, user_info['issues_url'][:-9]).display()
    elif options.gists:
        pass
        # RepoInfoDisplayObject(user_info).display()
        # nl()
        # o = CommitDisplayFactory.forCommit(
        #     options.commits, user_info['commits_url'][:-6]).display()
    elif options.following:
        pass
    elif options.followers:
        pass


class UserInfoDisplayObject(DisplayObject):
    def __init__(self, user_data):
        super().__init__(user_data)

    def display(self):
        boxed("{} (@{})".format(self.data['name'], self.data['login']))
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
            putEntry('Website', 'https://' +
                     self.data['blog'], valueColor=blue)
            nl()
        putEntry('Number of (public) repos', self.data['public_repos'])
        putEntry('Number of (public) gists', self.data['public_gists'])
        nl()
        putEntry('Followers', self.data['followers'])
        putEntry('Following', self.data['following'])
