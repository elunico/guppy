#!/usr/bin/python3

import sys
import requests
import argparse
from colors import *
from utils import *
from repo_display import *
from user_display import *


def dispatch():
    # todo: formatting help messages: use colors and indent/wrap
    if len(sys.argv) < 2:
        print(usage)
        return
    elif sys.argv[1] == 'help':
        print(usage)
        print(
            '{} user USER: retrieve information for USER. Use `user -h` for more information'.format(sys.argv[0]))
        print(
            '{} repo USER/REPO: retrieve information about REPO. Note that it must be qualified by a username. Use `repo -h` for more information'.format(sys.argv[0]))
        print('{} help: print this message'.format(sys.argv[0]))
    elif sys.argv[1] == 'user':
        if len(sys.argv) < 3:
            print("Error must specify USER for user mode")
            return
        info_user(*sys.argv[2:])
    elif sys.argv[1] == 'repo':
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


if __name__ == '__main__':
    main()
