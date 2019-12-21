from utils import *
from colors import *
from display import *


class UserFollowDisplayObjectFactory:
    @staticmethod
    def forFollow(user, kind, following, url):
        if following == 'all':
            all_following = []
            all_following_pages = get_all_pages_warned(
                user, url, kind)
            for v in all_following_pages.values():
                all_following.extend(v)
            if not all_following:
                return NoFollowDisplayObject()
            return UserFollowMultipleDisplayObject(all_following)
        elif following[0] == 'p':
            pages = parse_pages(following)
            all_following = []
            all_following_pages = get_all_data_pages(user, pages, url, kind)
            for v in all_following_pages.values():
                all_following.extend(v)
            if not all_following:
                return NoFollowDisplayObject()
            return UserFollowMultipleDisplayObject(all_following)
        else:
            putln(red,
                  'User python guppy.py user USERNAME to see information for a specific user')
            clear()


class NoFollowDisplayObject(DisplayObject):
    def __init__(self):
        super().__init__({})

    def display(self):
        putln(yellow + bold, "No accounts found.")
        clear()


class UserFollowMultipleDisplayObject(DisplayObject):
    def __init__(self, data):
        super().__init__(data)

    def display(self):
        for following in self.data:
            UserFollowSingleDisplayObject(following).display()
            nl()
            putln(black, '=' * CONSOLE_WIDTH)


class UserFollowSingleDisplayObject(DisplayObject):
    def __init__(self, data):
        super().__init__(data)

    def display(self):
        login = self.data['login']
        link = self.data['html_url']
        putEntry('Username', login)
        putEntry('Link', link, valueColor=blue)
