#!/usr/bin/env python3

import sys
from colors import *
from utils import *
from repo_display import *
from user_display import *
from caching import *


def dispatch():
    """
    Checks initial arugments (MODE and ARGUMENT) and dispatches to the correct function for further processing
    """
    if len(sys.argv) < 2:
        print(usage)
        return 1
    elif sys.argv[1].lower() == 'help':
        print(usage)
        nl()
        LongTextDisplayObject('{0}{1} user USER{2}: retrieve information for USER. Use `user -h` for more information'.format(
            bold, sys.argv[0], black), CONSOLE_WIDTH - 2, 2).display()
        nl()
        LongTextDisplayObject('{0}{1} repo USER/REPO{2}: retrieve information about REPO. Note that it must be qualified by a username. Use `repo -h` for more information'.format(
            bold, sys.argv[0], black), CONSOLE_WIDTH - 2, 2).display()
        nl()
        LongTextDisplayObject('{0}{1} cache OPTIONS{2}: retrieve information about the cache and change settings regarding it. Try ./guppy cache help for more information'.format(
            bold, sys.argv[0], black), CONSOLE_WIDTH - 2, 2).display()
        nl()
        print('  {}{} help{}: print this message'.format(
            bold, sys.argv[0], black))
        nl()
        dispatch_result = 0
    elif sys.argv[1].lower() == 'cache':
        if len(sys.argv) < 3:
            perror("Error must specify action for cache mode")
            return 20
        dispatch_result = cache_action(sys.argv[2])
    elif sys.argv[1].lower() == 'user':
        if len(sys.argv) < 3:
            perror("Error must specify a username for user mode")
            return 30
        dispatch_result = info_user(*sys.argv[2:])
    elif sys.argv[1].lower() == 'repo':
        if len(sys.argv) < 3:
            perror("Error must specify USER/REPO for repo mode")
            return 40
        if '/' not in sys.argv[2]:
            perror("Error must specify USER/REPO for repo mode")
            return 50
        dispatch_result = info_repo(*sys.argv[2:])
    else:
        perror(usage)
        dispatch_result = 200

    assert type(dispatch_result) is int
    return dispatch_result


def main():
    result = dispatch()
    # CACHE_END MUST BE CALLED BEFORE THE PROGRAM EXITS
    # BUT AFTER *ALL* CACHE ACTIONS HAVE BEEN PERFORMED
    # TO ENSURE THE CORRECT FUNCTIONALITY OF THE CACHE
    cache_result = cache_end()

    if result and cache_result:
        return int(cache_result) << 8 | result

    return result if result else cache_result


if __name__ == '__main__':
    raise SystemExit(main())
