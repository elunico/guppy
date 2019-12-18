from utils import *
from display import *


class UserGistsDisplayObjectFactory:
    @staticmethod
    def forGists(gists, gists_url):
        if gists == 'all':
            all_gists = get_all_pages_warned(gists_url)
            if not all_gists:
                return NoGistsDisplayObject()
            return MultipleGistsDisplayObject(all_gists)
        else:
            if 'p' in gists:
                pages = parse_pages(gists)
                all_gists = get_all_data_pages(oages, gists_url)
                if not all_gists:
                    return NoGistsDisplayObject()
                return MultipleGistsDisplayObject(all_gists)
            else:
                gist_info = requests.get(
                    '{}/{}'.format(gists_url, gists)).json()
                if not gist_info:
                    return NoGistsDisplayObject()
                return SingleGistDisplayObject()


class NoGistsDisplayObject(DisplayObject):
    def __init__(self, data):
        super().__init__(data)

    def display(self):
        putln(yellow + bold, 'No gists found.')
        clear()


class MultipleGistsDisplayObject(DisplayObject):
    def __init__(self, data):
        super().__init__(data)

    def display(self):
        pass


class SingleGistDisplayObject(DisplayObject):
    def __init__(self, data):
        super().__init__(data)

    def display(self):
        pass
