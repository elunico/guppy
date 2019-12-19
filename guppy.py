#!/usr/bin/python3

import sys
import requests
import argparse
from colors import *
from utils import *
from repo_display import *
from user_display import *
from caching import *


def dispatch():
    if len(sys.argv) < 2:
        print(usage)
        return
    elif sys.argv[1].lower() == 'help':
        print(usage)
        nl()
        LongTextDisplayObject('{0}{1} user USER{2}: retrieve information for USER. Use `user -h` for more information'.format(
            bold, sys.argv[0], black), CONSOLE_WIDTH - 2, 2).display()
        nl()
        LongTextDisplayObject('{0}{1} repo USER/REPO{2}: retrieve information about REPO. Note that it must be qualified by a username. Use `repo -h` for more information'.format(
            bold, sys.argv[0], black), CONSOLE_WIDTH - 2, 2).display()
        nl()
        print('  {}{} help{}: print this message'.format(
            bold, sys.argv[0], black))
        nl()
    elif sys.argv[1].lower() == 'cache':
        if len(sys.argv) < 3:
            print("Error must specify action for cache mode")
            return
        cache_action(sys.argv[2])
    elif sys.argv[1].lower() == 'user':
        if len(sys.argv) < 3:
            print("Error must specify USER for user mode")
            return
        info_user(*sys.argv[2:])
    elif sys.argv[1].lower() == 'repo':
        if len(sys.argv) < 3:
            print("Error must specify USER/REPO for repo mode")
            return
        if '/' not in sys.argv[2]:
            print("Error must specify USER/REPO for repo mode")
            return
        info_repo(*sys.argv[2:])
    else:
        print(usage)


def main():
    dispatch()
    cache_end()


if __name__ == '__main__':
    main()
