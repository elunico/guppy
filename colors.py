magenta = '\033[95m'
blue = '\033[94m'
green = '\033[92m'
yellow = '\033[93m'
red = '\033[91m'
black = '\033[0m'
bold = '\033[1m'
uline = '\033[4m'

from typing import List


def puts(color: str, *msgs: str, sep=' '):
    print("{}{}".format(color, sep.join(msgs)), end='')


def putln(color: str, *msgs: str, sep=' '):
    print("{}{}".format(color, sep.join(msgs)))


def nl():
    print()


def clear():
    print(black, end='')


def color_for_license(license):
    if license['key'] in ['mit', 'unlicense', 'wtfpl', 'gpl-2.0', 'lgpl-2.1', 'mpl-2.0', 'apache-2.0']:
        return green
    else:
        return yellow


def putEntry(key, value, keyColor=bold, valueColor=black):
    putln("{}{}: {}{}".format(keyColor, key, valueColor, value))
    clear()
