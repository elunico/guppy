import os.path
import os
import msgpack
import time
from typing import Union
from typing import Optional
from typing import Dict

user_home = os.path.expanduser('~')
cache_path = os.path.join(user_home, '.guppy', 'caches')
state_path = os.path.join(user_home, '.guppy', 'state')
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
    return msgpack.packb(data)


def unserialize(data):
    b = msgpack.unpackb(data)
    if isinstance(b, dict):
        ret = {}
        for (k, v) in b.items():
            if isinstance(k, bytes):
                k = str(k, encoding='utf-8')
            if isinstance(v, bytes):
                v = str(v, encoding='utf-8')
            ret[k] = v
        return ret
    else:
        assert isinstance(b, list)
        ret = []
        for item in b:
            if isinstance(item, bytes):
                item = str(item, encoding='utf-8')
            ret.append(item)
        return ret


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
    state = f.read()
with open(size_path) as f:
    size = size_for(f.read())


def prune_max_size():
    global index
    entries = sorted(list(index.items()), key=lambda x: x[1])
    while get_cache_size() > size and len(entries) > 0:
        path = str(entries.pop(0)[0], encoding='utf-8')
        path = cacheTo(path)
        assert '.guppy' in path
        os.remove(path)

    index = {k: v for (k, v) in entries}


def cache_language(qrepo: str, data: dict) -> int:
    prune_max_size()
    path = 'repo:{}.lang'.format(qrepo)
    index[path] = time.time()
    with open(cacheTo(path), 'wb') as f:
        return f.write(serialize(data))


def cache_user(username: str, data: dict) -> int:
    prune_max_size()
    path = 'user:{}'.format(username)
    index[path] = time.time()
    with open(cacheTo(path), 'wb') as f:
        return f.write(serialize(data))


def cache_repo(qrepo: str, data: dict) -> int:
    prune_max_size()
    path = 'repo:{}'.format(qrepo)
    index[path] = time.time()
    with open(cacheTo(path), 'wb') as f:
        return f.write(serialize(data))


def get_cached_language(qrepo: str, data: dict) -> int:
    path = 'repo:{}.lang'.format(qrepo)
    if os.path.exists(cacheTo(path)):
        with open(cacheTo(path), 'rb') as f:
            return unserialize(f.read())
    return None


def get_cached_user(username: str) -> Optional[dict]:
    path = 'user:{}'.format(username)
    if os.path.exists(cacheTo(path)):
        with open(cacheTo(path), 'rb') as f:
            return unserialize(f.read())
    return None


def get_cached_repo(qrepo: str) -> Optional[dict]:
    path = 'repo:{}'.format(qrepo)
    if os.path.exists(cacheTo(path)):
        with open(cacheTo(path), 'rb') as f:
            return unserialize(f.read())
    return None


def cache_action(action: str):
    action = action.lower()
    if action == 'clear':
        pass
    elif action == 'check':
        print("Cache state: {}".format(state))
        print("Cache max size: {:,} bytes".format(size))
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
