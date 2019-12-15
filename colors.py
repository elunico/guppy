magenta = '\033[95m'
blue = '\033[94m'
green = '\033[92m'
yellow = '\033[93m'
red = '\033[91m'
black = '\033[0m'
bold = '\033[1m'
uline = '\033[4m'


def puts(color, *msgs, sep=' '):
    print("{}{}".format(color, sep.join(msgs)), end='')


def putln(color, *msgs, sep=' '):
    print("{}{}".format(color, sep.join(msgs)))


def nl():
    print()


def clear():
    print(black, end='')


def color_for_license(license):
    if license['spdx_id'] in ['GPL-2.0', 'GPL-2.1', 'WTFPL', 'MIT']:
        return green
    else:
        return yellow
