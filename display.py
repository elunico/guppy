import textwrap
import os
import subprocess
from colors import *
# from utils import


try:
    if 'COLUMNS' in os.environ:
        CONSOLE_WIDTH = int(os.environ['COLUMNS'])
    elif os.system('stty size > /dev/null 2>&1') == 0:
        CONSOLE_WIDTH = int(subprocess.getstatusoutput(
            'stty size')[1].split()[1])
    else:
        CONSOLE_WIDTH = 80
except (IndexError, ValueError, AttributeError):
    CONSOLE_WIDTH = 80


def boxed(msg, center=CONSOLE_WIDTH - 4):
    items = msg.splitlines()
    print('-' * CONSOLE_WIDTH)
    for line in items:
        line = line.center(center)
        print("| {} |".format(line))
    print('-' * CONSOLE_WIDTH)


class DisplayObject:
    def __init__(self, data):
        self.data = data

    def display(self):
        raise NotImplementedError(
            'Implement Display on subclass of DisplayObject')


class LongTextDisplayObject(DisplayObject):
    def __init__(self, string, width, places):
        super().__init__(string)
        self.width = width
        self.places = places

    def wrap(self, string):

        return '\n'.join(
            ['\n'.join(textwrap.wrap(line, self.width))
                for line in string.split('\n') if line.strip()]
        )

        # return '\n'.join(textwrap.wrap(string, width=self.width))

    def indent(self, string, places):
        return textwrap.indent(string, ' ' * places)

    def display(self, colorString=black):
        putln(colorString, self.indent(self.wrap(self.data), self.places))
        clear()


class TitleDisplayer:
    def show_title(self, string):
        raise NotImplementedError('Abstract Class')


class BoxedTitleDisplayer(TitleDisplayer):
    def show_title(self, string):
        boxed(string)


class PlainTitleDisplayer(TitleDisplayer):
    def show_title(self, string):
        putln(bold, string)


def program_name():
    print("~*~*~*~* G I T H U B    C O N S O L E *~*~*~*~".center(CONSOLE_WIDTH))


def commify(numberText: str) -> str:
    return '{:,}'.format(numberText)


def fmt_bytes(bytes: int) -> str:
    if bytes > 1000000000:
        return '{:.2f} GB'.format(bytes / 1000000000)
    if bytes > 1000000:
        return '{:.2f} MB'.format(bytes / 1000000)
    if bytes > 1000:
        return '{:.2f} KB'.format(bytes / 1000)
    return "{} B".format(bytes)
