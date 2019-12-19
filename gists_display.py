from utils import *
from display import *
from user_display import *


class UserGistsDisplayObjectFactory:
    @staticmethod
    def forGists(gists, gists_url):
        if gists == 'all':
            all_gists = []
            all_gists_pages = get_all_pages_warned(gists_url)
            for v in all_gists_pages.values():
                all_gists.extend(v)
            if not all_gists:
                return NoGistsDisplayObject()
            return MultipleGistsDisplayObject(all_gists)
        else:
            if 'p' in gists:
                pages = parse_pages(gists)
                all_gists = []
                all_gists_pages = get_all_data_pages(gists, gists_url)
                for v in all_gists_pages.values():
                    all_gists.extend(v)
                if not all_gists:
                    return NoGistsDisplayObject()
                return MultipleGistsDisplayObject(all_gists)
            else:
                gurl = 'https://api.github.com/gists/{}'.format(gists)
                gist_info = requests.get(gurl).json()
                if not response_check(gist_info, 'gist'):
                    return NoGistsDisplayObject()
                if not gist_info:
                    return NoGistsDisplayObject()
                return SingleExtraGistDisplayObject(gist_info)


class NoGistsDisplayObject(DisplayObject):
    def __init__(self):
        super().__init__({})

    def display(self):
        putln(yellow + bold, 'No gists found.')
        clear()


class MultipleGistsDisplayObject(DisplayObject):
    def __init__(self, data):
        super().__init__(data)

    def display(self):
        for gist in self.data:
            SingleGistDisplayObject(
                gist, titler=PlainTitleDisplayer()).display()
            nl()
            print('=' * CONSOLE_WIDTH)
            nl()


class SingleGistDisplayObject(DisplayObject):
    def __init__(self, data, titler=BoxedTitleDisplayer()):
        super().__init__(data)
        self.titler = titler

    def display(self):
        repo_info = self.data
        url = self.data['html_url']
        owner = self.data['owner']['login']
        comments = self.data['comments']
        updated = formatted_time(repo_info['updated_at'])
        created = formatted_time(repo_info['created_at'])
        files = len(self.data['files'].keys())
        self.titler.show_title("gist: {}".format(self.data['id']))
        # putEntry('ID (for query)', self.data['id'])
        putEntry('URL', url, valueColor=blue)
        putEntry('Owned by', owner)
        nl()
        putEntry('Created Updated', created, valueColor=yellow)
        putEntry('Last Updated', updated, valueColor=green)
        clear()
        nl()
        putEntry('Comments', comments)
        nl()
        putEntry('Files', files)
        clear()


class SingleExtraGistDisplayObject(DisplayObject):
    def __init__(self, data):
        super().__init__(data)

    def display(self):
        SingleGistDisplayObject(self.data).display()

        for (file, data) in self.data['files'].items():
            putEntry('  Name', data['filename'], valueColor=magenta)
            putEntry('  Language', data['language'])
            putEntry('  Size', data['size'])

        nl()
        putln(bold, "Description:")
        desc = self.data['description']
        if not desc:
            putln(magenta, 'No description.')
        else:
            LongTextDisplayObject(desc, CONSOLE_WIDTH - 2, 2).display(magenta)
        clear()
