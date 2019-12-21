magenta = '\033[95m'
blue = '\033[94m'
green = '\033[92m'
yellow = '\033[93m'
red = '\033[91m'
black = '\033[0m'
bold = '\033[1m'
uline = '\033[4m'

from typing import List
import os


def puts(color: str, *msgs: str, sep=' '):
    print("{}{}".format(color, sep.join(msgs)), end='')


def putln(color: str, *msgs: str, sep=' '):
    print("{}{}".format(color, sep.join(msgs)))


def nl():
    print()


def clear():
    """
    Clears the current output color. Does NOT clear the terminal
    """
    print(black, end='')


def color_for_license(license: dict):
    if license['key'] in ['mit', 'unlicense', 'wtfpl', 'gpl-2.0', 'lgpl-2.1', 'mpl-2.0', 'apache-2.0']:
        return green
    else:
        return yellow


def putEntry(key, value, keyColor=bold, valueColor=black):
    """
    Write a key value pair to the console in a nicely formatted way
    """
    putln("{}{}: {}{}".format(keyColor, key, valueColor, value))
    clear()


if os.environ.get('DEBUG', False):

    import inspect
    import os.path

    def line():
        return "{}:{}:{}".format(os.path.split(inspect.stack()[2][1])[-1], inspect.stack()[2][2],
                                 inspect.stack()[2][3])

    def debug(msg, color=black):
        print("{2}DEBUG: {0} {1}{3}".format(line(), msg, color, black))
else:
    def line(): return ''

    def debug(*args, **kwargs): pass
