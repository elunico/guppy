# Guppy

Guppy is a tool for getting information about GitHub repos and users on the command line.

It is named guppy for two reasons. 1) guppy ends in py and guppy is written in Python. 2) It is a play on GitHub-y (a reach maybe).

## Dependencies

Guppy depends only on a `python3` installation. I used `3.6.0` to develop it so it should work on anything `3.6.0` or later. It will not work on `2` and it may work earlier than `3.6.0`.

## Usage

Once cloned or downloaded, simply `cd` into the folder and use
`python3 guppy.py MODE ARUGMENT [OPTIONS...]`

`MODE` can be `repo` or `user`. Currently `user` is not implemented but it will allow you to retrieve
information on users. `repo` allows you to retrieve information on a repository.

`ARGUMENT` is the repo or user that you want to get information about.
For users it has the form `USERNAME` and for repos it has the form `USERNAME/REPO`

`[OPTIONS...]` are optional additional options regarding what information should be returned
and printed to the console.

### Options

For repositories
- `-i ISSUE` Get information about the issues in the repo. use `-i all` to see all issues or `-i NUMBER` to see a particular issue.
- `-c COMMIT` Get information about the commits in the repo. use `-c all` to see all commits or `-i HASH` to see a particular commit.

more options may be added in the future

## Example

`./guppy.py repo elunico/SocDraw -i 3`

![Screenshot of example 1 command](/assets/issue-example.png?raw=true " ")

`python3 guppy.py repo elunico/guppy`

![Screenshot of example 2 command](/assets/repo-example.png?raw=true " ")

## IMPORTANT!!

Unauthetincated requests using GitHub's API are limited to 60 per hour. Currently, this tool interfaces directly with the GitHub API in an unathenticated way. This will change later but for now keep this in mind as you use this tool. Your IP address will be cut off from `api.github.com` after 60 requests within an hour.

Also keep in mind that one run of the program may result in **mutliple requests**. For example,
to retrieve all commits requires getting the repo information and the commit information. The
regular screen for information on a repo requires a request to get the repo information
and the language information
