import os.path
import os
import msgpack
import time
from colors import *
from utils import *
from typing import Union
from typing import Optional
from typing import Dict

############
# Qualified repo names (user/repo) are stored in files as `user$repo`
# due to limitations of filesystems around files containing `/`
############

user_home = os.path.expanduser('~')
cache_path = os.path.join(user_home, '.guppy', 'caches')
state_path = os.path.join(user_home, '.guppy', 'CACHING_ACTIVE')
size_path = os.path.join(user_home, '.guppy', 'size')
index_path = os.path.join(user_home, '.guppy', 'cache_index')


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


def cacheTo(*args):
    return os.path.join(cache_path, *args)


TimeStamp = float
FileName = str

if not os.path.exists(index_path):
    index: Dict[FileName, TimeStamp] = {}
else:
    with open(index_path, 'rb') as f:
        index = unserialize(f.read())

if not os.path.isdir(cache_path):
    os.makedirs(cache_path)

if not os.path.exists(state_path):
    with open(state_path, 'w') as f:
        f.write('start')

if not os.path.exists(size_path):
    with open(size_path, 'w') as f:
        f.write('100m')


def size_for(s):
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


with open(state_path) as f:
    CACHING_ACTIVE = f.read() == 'start'
with open(size_path) as f:
    MAX_CACHE_SIZE = size_for(f.read())


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


def cache_language(qrepo: str, data: dict) -> int:
    prune_max_size()
    if '/' in qrepo:
        qrepo = qrepo.replace('/', '$')
    path = 'repo.{}.lang'.format(qrepo)
    index[path] = time.time()
    with open(cacheTo(path), 'wb') as f:
        return f.write(serialize(data))


def cache_user(username: str, data: dict) -> int:
    prune_max_size()
    path = 'user.{}'.format(username)
    index[path] = time.time()
    with open(cacheTo(path), 'wb') as f:
        return f.write(serialize(data))


def cache_repo(qrepo: str, data: dict) -> int:
    prune_max_size()
    if '/' in qrepo:
        qrepo = qrepo.replace('/', '$')
    path = 'repo.{}'.format(qrepo)
    index[path] = time.time()
    with open(cacheTo(path), 'wb') as f:
        return f.write(serialize(data))


def cache_issue(qrepo: str, id: str, data: dict) -> int:
    raise NotImplementedError()


def cache_commit(qrepo: str, sha: str, data: dict) -> int:
    raise NotImplementedError()


def cache_repo_list(qrepo: str, list: str, page: str, data: list) -> int:
    '''
    `list` param should be issues or commits
    '''
    qrepo = qrepo.replace('/', '$')
    prune_max_size()
    path = 'repo.{}.{}.{}'.format(user, list, page)
    index[path] = time.time()
    with open(cacheTo(path), 'wb') as f:
        return f.write(serialize(data))


def cache_user_list(user: str, list: str, page: str, data: list) -> int:
    '''
    `list` param should be repos or gists
    '''
    prune_max_size()
    path = 'user.{}.{}.{}'.format(user, list, page)
    index[path] = time.time()
    with open(cacheTo(path), 'wb') as f:
        return f.write(serialize(data))


def get_cached_user_list(user: str, list: str, page: str) -> Optional[list]:
    '''
    `list` param should be repos or gists
    '''
    path = 'user.{}.{}.{}'.format(user, list, page)
    if os.path.exists(cacheTo(path)):
        with open(cacheTo(path), 'rb') as f:
            return unserialize(f.read())
    return None


def get_cached_issue(qrepo: str, id: str) -> int:
    raise NotImplementedError()


def get_cached_commit(qrepo: str, id: str) -> int:
    raise NotImplementedError()


def get_cached_language(qrepo: str) -> Optional[dict]:
    if '/' in qrepo:
        qrepo = qrepo.replace('/', '$')
    path = 'repo.{}.lang'.format(qrepo)
    if os.path.exists(cacheTo(path)):
        with open(cacheTo(path), 'rb') as f:
            return unserialize(f.read())
    return None


def get_cached_user(username: str) -> Optional[dict]:
    path = 'user.{}'.format(username)
    if os.path.exists(cacheTo(path)):
        with open(cacheTo(path), 'rb') as f:
            return unserialize(f.read())
    return None


def get_cached_repo(qrepo: str) -> Optional[dict]:
    if '/' in qrepo:
        qrepo = qrepo.replace('/', '$')
    path = 'repo.{}'.format(qrepo)
    if os.path.exists(cacheTo(path)):
        with open(cacheTo(path), 'rb') as f:
            return unserialize(f.read())
    return None


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
        print("Cache CACHING_ACTIVE: {}".format(CACHING_ACTIVE))
        print("Cache max size: {:,} bytes".format(MAX_CACHE_SIZE))
        csize = get_cache_size()
        print("Cache current size: {:,} bytes".format(csize))
    elif action == 'start':
        with open(state_path, 'w') as f:
            f.write('start')
    elif action == 'stop':
        with open(state_path, 'w') as f:
            f.write('stop')
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
    with open(index_path, 'wb') as f:
        f.write(serialize(index))
