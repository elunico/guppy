import textwrap
from colors import *
from utils import *


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
        return '\n'.join(textwrap.wrap(string, width=self.width))

    def indent(self, string, places):
        return textwrap.indent(string, ' ' * places)

    def display(self, colorString=black):
        putln(colorString, self.indent(self.wrap(self.data), self.places))
        clear()


def title():
    print("~*~*~*~* G I T H U B    C O N S O L E *~*~*~*~".center(CONSOLE_WIDTH))
