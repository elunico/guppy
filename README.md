# Guppy

`[active development]`

Guppy is a tool for getting information about GitHub repos and users on the command line.

It is named guppy for two reasons. 1) guppy ends in py and guppy is written in Python. 2) It is a play on GitHub-y (a reach maybe).

## Dependencies

*You can use `pip install -r requirements.txt` to install dependencies. It is recommended to use a virtualenv for dependency management.*

#### Guppy requires the following things

- A `python 3` installation.
  - Guppy was created using `3.6.0` so it should work on anything `3.6.0` or later. It will not work on `2` and it might or might not work on versions earlier than `3.6.0`.

- **The `requests` module.** You can install it with `pip install requests`.
  - The `requests` module is a friendly way of doing `http(s)` requests that is easier to interface with than python's `urllib` module.

- **The `dateutil.parser` module.** You can install it with  `pip install python-dateutil`.
  - This is used to show times in a locale-friendly way.

- **The `msgpack` module.** You can install it with `pip install msgpack`.
  - MessagePack is a data serialization format similar to JSON but it uses binary data instead of human readable data making it more compact. It is used for caching data in guppy.


## Usage

Once cloned or downloaded, and all the dependencies are installed, simply `cd` into the folder and use
`python3 guppy.py MODE ARUGMENT [OPTIONS...]`

`MODE` can be `repo`, `user`, or `cache`.

- `user` allows you to retreive information around users
- `repo` allows you to retrieve information on a repository.

For more information on what additional information you can retrieve, see below.

- `cache` allows you to get information and control the settings of the cache. Guppy will cache the data it fetches from GitHub's servers for some time to make data faster to access, and to avoid GitHub's rate limiting. It is stored in `~/.guppy/caches/` where `~` is the home folder of the user running Guppy. It stores additional data including settings and an index of the cache in `~/.guppy/`. Cache data expires after 1 day by default but this can be changed. Cache items are not removed until the program is rerun after their expiration date, and can be manually cleared at any time.

`ARGUMENT` is the repo or user that you want to get information about.
- For users it has the form `USERNAME`
- For repos it has the form `OWNER/REPO`, where `OWNER` is the username of the person who owns `REPO`

*Providing this argument without additional `OPTIONS` will show summary information on the user or repo that is specified.*

- For cache mode, it has the form `(start | stop | check | size:nD | time:nD | clear)`. Meaning you can pass one of these four options to take some action with the cache

`[OPTIONS...]` are optional additional options regarding what information should be returned and printed to the console. More information can be found below.
*Note: options are not allowed for `cache` mode*

### Options

For repositories in `repo` mode
- `-i ISSUE` Get information about the issues in the repo. use `-i all` to see all issues (or several if there are many), `-i NUMBER` to see a particular issue, or `-i pPAGE_SPEC` for a particular page or pages
- `-c COMMIT` Get information about the commits in the repo. use `-c all` to see all commits (or several if there are many),  `-c HASH` to see a particular commit, or `-c pPAGE_SPEC` to see a particular page or pages.
  - You can also specify `-c HEAD`. This will fetch the head commit of the default branch of the repo and then display it. This option always makes a request to find the HEAD commit, but if it is cached, it will retrieve it from the cache.
- `-b BRANCH` Get information about the branches in the repo. Use `-b all` to see all branches (or several if there are many),  `-b NAME` to see a particular branch, or `-b pPAGE_SPEC` to see a particular page or pages.

For users in `user` mode
- `-g GIST` Get information about the gists of the user. use `-g all` to see all gists (or several if there are many), `-g ID` to see a particular gist, or `-g pPAGE_SPEC` for a particular page or pages
- `-r REPO` Get information about the repos of the user. use `-r all` to see all repos (or several if there are many) or `-r pPAGE_SPEC` to see a particular page or pages. To see a particular repo, refer to `repo` mode.
- `--following FOLLOW` Get information about the people the user follows. use `--following all` to see all the people they follow (or several if there are many) or `-i pPAGE_SPEC` for a particular page or pages. To see a particular user, use regular `user` mode
- `--followers FOLLOW` Get information about the user's followers. use `--followers all` to see all the usere's followers (or several if there are many) or `-i pPAGE_SPEC` for a particular page or pages. To see a particular follower, use regular `user` mode

more options may be added in the future

For `cache` mode
- `start` indicates you wish to use caching. Data will be kept for the specified amount of time (1 day default) but no more than the maximum amount of data will be kept (10 MB by default).
- `stop` indicates you do not want any cache access. All invocations of the program will make requests ot GitHub. No cache data will be removed by this option.
- `clear` removes all data from the cache.
- `size:nD` changes the maximum size of the cache. `n` is a number and `D` is a denomination. `D` can be `k` for kilobytes, `m` for megabytes, or `g` for gigabytes. You can also leave it off to indicate bytes. So, for instance, `30m` would be 30 megabytes `100k` is 100 kilobytes etc.
- `time:nD` changes the maximum amount of time to keep data in the cache. `n` is a number and `D` is a denomination. `D` can be `m` for minutes, `h` for hours, `d` for days. You can leave it off for seconds. For instnace, `30m` indicates cache data will be deleted after 30 minutes. `1d` indicates cache data will be deleted after 1 day (24 hours), etc.

## `PAGE_SPEC`

"What does `pPAGE_SPEC` mean in those options above?" you may be asking.  Well, the `p` at the beginning, being lowercase, is a literal `p` meaning that, in order to specify pages, you must prefix the `PAGE_SPEC` with a literal character `p`.

Ok, but what is a `PAGE_SPEC`? `PAGE_SPEC` is what I am calling a particular method of specifying a group of several pages that you may already be familiar with, thanks to Microsoft Word.

It is a string of comma or hypen separated numbers that indicate a group of pages. Numbers separated by a comma indicate individual pages and numbers separated by a dash indicate a consecutive, inclusive range of pages.

For example,

`1` indicates page 1.

`1,2,3,4` indicates pages 1, 2, 3, and 4

`1-4` also indicates pages 1, 2, 3, and 4

`1,2,3,5-9` indicates pages 1, 2, 3, 5, 6, 7, 8, and 9.

`1,3-8,14` indicates pages 1, 3, 4, 5, 6, 7, 8, and 14.

and so on.

To use these in the program, remember they *must* be prefixed with `p`, otherwise they would be confused for the actual identifier of the resource.

For example:

`python guppy.py repo elunico/SocDraw -i 3`

indicates you want issue #3 of the repo `elunico/SocDraw`. However,

`python guppy.py repo elunico/SocDraw -i p3`

indicates you want the **third page** of issues from the repo `elunico/SocDraw`.


## Example

`./guppy.py repo elunico/SocDraw -i 3`

![Screenshot of example 1 command](/assets/issue-example.png?raw=true " ")

`python3 guppy.py repo elunico/guppy`

![Screenshot of example 2 command](/assets/repo-example.png?raw=true " ")

`python3 guppy.py user elunico`
![Screenshot of example 3 command](/assets/user-example.png?raw=true " ")

## IMPORTANT!!

Unauthetincated requests using GitHub's API are limited to 60 per hour. Currently, this tool interfaces directly with the GitHub API in an unathenticated way. This will change later but for now keep this in mind as you use this tool. Your IP address will be cut off from `api.github.com` after 60 requests within an hour.

Also keep in mind that one run of the program may result in **mutliple requests**. For example,
to retrieve all commits requires getting the repo information and the commit information. The
regular screen for information on a repo requires a request to get the repo information
and the language information

## Disclaimer

This program is being actively developed and it is likely many things will change. Nothing about the command line options, access, input, or output should be expected to stay the same until development ends
