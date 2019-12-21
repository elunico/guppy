import os.path
import os
import msgpack
import time
from colors import *
from display import commify, fmt_bytes
from typing import Union
from typing import Optional
from typing import Dict

############
# Qualified repo names (user/repo) are stored in files as `user-repo`
# due to limitations of filesystems around files containing `/`
############

# locations of cache data, index, state, and other settings
user_home = os.path.expanduser('~')
cache_path = os.path.join(user_home, '.guppy', 'caches')
state_path = os.path.join(user_home, '.guppy', 'state')
size_path = os.path.join(user_home, '.guppy', 'size')
index_path = os.path.join(user_home, '.guppy', 'cache_index')
time_path = os.path.join(user_home, '.guppy', 'max_seconds')


def get_cache_size():
    s = 0
    for f in os.listdir(cache_path):
        path = os.path.join(cache_path, f)
        if os.path.isfile(path):
            s += os.path.getsize(path)
    return s


def serialize(data):
    # use_bin_type tells msgpack to distinguish str and bytes
    return msgpack.packb(data, use_bin_type=True)


def unserialize(data):
    # raw=False tells msgpack to convert str back into str not keep as bytes
    return msgpack.unpackb(data, raw=False)


# returns the args path joined to cache_path. Used get the path to a cache file
# given the filename only
def cacheTo(*args):
    return os.path.join(cache_path, *args)


TimeStamp = float
FileName = str

# read in the index or create a blank one if none exists
if not os.path.exists(index_path):
    index: Dict[FileName, TimeStamp] = {}
else:
    with open(index_path, 'rb') as f:
        index = unserialize(f.read())

# create dirs for cache storage
if not os.path.isdir(cache_path):
    os.makedirs(cache_path)

# later we will read in the settings from these files
# if the files are not present we first write defaults
# this allows defaults to be present and prevents errors on first read
if not os.path.exists(state_path):
    with open(state_path, 'w') as f:
        f.write('start')

if not os.path.exists(size_path):
    with open(size_path, 'w') as f:
        f.write('100m')

if not os.path.exists(time_path):
    with open(time_path, 'w') as f:
        f.write('86400')


def size_for(s):
    """
    This function takes a string representing an amount of bytes and converts
    it into the int corresponding to that many bytes. The string can be a plain
    int which gets directly converted to that number of bytes or can end in a specifier
    such as 100k. This indicates it is 100 kilobytes and so is translated into 100000

    for example
    size_for('1000') == 1000
    size_for('10m') == 10000000
    size_for('1000k') == size_for('1m')
    etc.

    The valid specifiers are
    k = kilo (1000)
    m = mega (1000000)
    g = giga (1000000000)
    """
    s = s.strip()
    try:
        return int(s)
    except ValueError:
        pass
    d = s[-1]
    v = s[:-1]
    m = 1
    if d == 'k':
        m = 1000
    elif d == 'm':
        m = 1000000
    elif d == 'g':
        m = 1000000000
    return int(v) * m


# read in settings
with open(state_path) as f:
    CACHING_ACTIVE = f.read() == 'start'
with open(size_path) as f:
    MAX_CACHE_SIZE = size_for(f.read())
with open(time_path) as f:
    MAX_CACHE_SECONDS = float(f.read())


# this function removes records that are too old (expired)
def prune_expired_caches():
    global index
    entries = sorted(list(index.items()), key=lambda x: x[1])
    now = time.time()
    # index is sorted by time, oldest times towards 0
    # while the oldest items are older than the MAX
    # remove those items
    while len(entries) > 0 and now - entries[0][1] > MAX_CACHE_SECONDS:
        path = cacheTo(entries.pop(0)[0])
        assert '.guppy' in path
        try:
            os.remove(path)
            debug('Removing {} because it is too old'.format(path), magenta)
        except FileNotFoundError:
            debug('File {} in index but not found on delete. '.format(path), yellow)

    index = {k: v for (k, v) in entries}


# anytime someone imports caching, and caching active according
# to user preference, we should prune expired caches
if CACHING_ACTIVE:
    prune_expired_caches()

# this function removes cache files until the size of the cache
# is less than the maximum specified


def prune_max_size():
    global index
    entries = sorted(list(index.items()), key=lambda x: x[1])
    while get_cache_size() > MAX_CACHE_SIZE and len(entries) > 0:
        path = cacheTo(entries.pop(0)[0])
        assert '.guppy' in path
        try:
            os.remove(path)
        except FileNotFoundError:
            debug('File {} in index but not found on delete. '.format(path), yellow)

    index = {k: v for (k, v) in entries}

# this function takes a filename and some data and stores the data
# at that file name in the cache directory


def cache_item(path, data):
    prune_max_size()
    index[path] = time.time()
    with open(cacheTo(path), 'wb') as f:
        return f.write(serialize(data))

# the following are several convenience functions for storing
# particular types of data by name that delegate to cache_item


def cache_language(qrepo: str, data: dict) -> int:
    qrepo = qrepo.replace('/', '-')
    path = 'repo.{}.lang'.format(qrepo)
    return cache_item(path, data)


def cache_user(username: str, data: dict) -> int:
    path = 'user.{}'.format(username)
    return cache_item(path, data)


def cache_repo(qrepo: str, data: dict) -> int:
    qrepo = qrepo.replace('/', '-')
    path = 'repo.{}'.format(qrepo)
    return cache_item(path, data)


def cache_issue(qrepo: str, id: str, data: dict) -> int:
    qrepo = qrepo.replace('/', '-')
    path = 'repo.{}.issue.{}'.format(qrepo, id)
    return cache_item(path, data)


def cache_commit(qrepo: str, sha: str, data: dict) -> int:
    qrepo = qrepo.replace('/', '-')
    path = 'repo.{}.commit.{}'.format(qrepo, sha)
    return cache_item(path, data)


def cache_repo_list(qrepo: str, list: str, page: str, data: list) -> int:
    '''
    `list` param should be issues or commits
    '''
    qrepo = qrepo.replace('/', '-')
    path = 'repo.{}.{}.p{}'.format(qrepo, list, page)
    return cache_item(path, data)


def cache_user_list(user: str, list: str, page: str, data: list) -> int:
    '''
    `list` param should be repos, gists, following, or followers
    '''
    path = 'user.{}.{}.p{}'.format(user, list, page)
    return cache_item(path, data)

# end convenience functions

# this function, given the filename of a cache file,
# returns the data in that file if it exists or None if it does not


def retrieve_cached_item(path):
    if os.path.exists(cacheTo(path)):
        with open(cacheTo(path), 'rb') as f:
            return unserialize(f.read())
    return None


# the following are several convenience functions for retrieving cache
# files by data name that delegate to retrieve_cached_item
def get_cached_repo_list(qrepo: str, list: str, page: str) -> int:
    '''
    `list` param should be issues or commits
    '''
    qrepo = qrepo.replace('/', '-')
    path = 'repo.{}.{}.p{}'.format(qrepo, list, page)
    return retrieve_cached_item(path)


def get_cached_user_list(user: str, list: str, page: str) -> Optional[list]:
    '''
    `list` param should be repos or gists
    '''
    path = 'user.{}.{}.p{}'.format(user, list, page)
    return retrieve_cached_item(path)


def get_cached_issue(qrepo: str, id: str) -> int:
    qrepo = qrepo.replace('/', '-')
    path = 'repo.{}.issue.{}'.format(qrepo, id)
    return retrieve_cached_item(path)


def get_cached_commit(qrepo: str, sha: str) -> int:
    qrepo = qrepo.replace('/', '-')
    path = 'repo.{}.commit.{}'.format(qrepo, sha)
    return retrieve_cached_item(path)


def get_cached_language(qrepo: str) -> Optional[dict]:
    qrepo = qrepo.replace('/', '-')
    path = 'repo.{}.lang'.format(qrepo)
    return retrieve_cached_item(path)


def get_cached_user(username: str) -> Optional[dict]:
    path = 'user.{}'.format(username)
    return retrieve_cached_item(path)


def get_cached_repo(qrepo: str) -> Optional[dict]:
    qrepo = qrepo.replace('/', '-')
    path = 'repo.{}'.format(qrepo)
    return retrieve_cached_item(path)

# end convenience functions


def clear_cache():
    global index
    c = 0
    for file in os.listdir(cache_path):
        os.remove(cacheTo(file))
        c += 1

    index = {}
    return c


def cache_action(action: str):
    action = action.lower()
    if action == 'clear':
        count = clear_cache()
        print("Deleted {} cached records.".format(count))
    elif action == 'check':
        print("Using cache?: {}".format(CACHING_ACTIVE))
        print("Cache max size: {}".format(fmt_bytes(MAX_CACHE_SIZE)))
        csize = get_cache_size()
        print("Cache current size: {} bytes".format(fmt_bytes(csize)))
    elif action == 'start':
        try:
            with open(state_path, 'w') as f:
                f.write('start')
        except Exception as e:
            print(red, 'Could not start caching: ' + str(e))
        else:
            print(
                green, 'Caching active! Previous, if any, and future cache data will be available starting now')
        clear()
    elif action == 'stop':
        try:
            with open(state_path, 'w') as f:
                f.write('stop')
        except Exception as e:
            print(red, 'Could not disable caching: ' + str(e))
        else:
            print(green, 'Caching stopped! Future invocations will always result in requests to Github. Use CLEAR option to clear existing caches.')
        clear()
    elif action.startswith('size:'):
        value = size_for(action[5:])
        with open(size_path, 'w') as f:
            f.write('{}'.format(value))
        print('Cache max size set to {:,} bytes'.format(value))
    elif action == 'help':
        print('Caching options for guppy:')
        print('  CLEAR   -> delete all cache files.')
        print('  STOP    -> stop caching data.')
        print('  START   -> begin caching data.')
        print('  CHECK   -> print current cache status.')
        print('  SIZE:nD -> Change the maximum size of the cache where n is the amount and D is the denomination: k (kilobytes), m (megabytes), g (gigabytes).')
    else:
        print("Invalid action {}. Try python3 guppy.py cache help")


def cache_end():
    """
    THIS FUNCTION MUST BE CALLED BEFORE THE PROGRAM QUITS
    BUT NOT BEFORE ANY FURTHER ACTION IS TAKEN ON THE CACHE
    IT IS CALLED, CURRENTLY RIGHT BEFORE THE PROGRAM EXISTS
    AFTER dispatch() IN guppy.py
    IT WRITES THE INDEX OF THE CACHE OUT AND WITHOUT THE
    CACHE CANNOT PRUNE ITSELF
    """
    with open(index_path, 'wb') as f:
        f.write(serialize(index))
