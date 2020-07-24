[![OS Compatibility][platform-badge]](#prerequisites)
[![Python Compatibility][python-badge]][python-dl]
[![pre-commit][pre-commit-badge]][pre-commit]
[![Code validation](https://github.com/ComplianceAsCode/auditree-plant/workflows/format%20%7C%20lint%20%7C%20test/badge.svg)][lint-test]
[![Upload Python Package](https://github.com/ComplianceAsCode/auditree-plant/workflows/PyPI%20upload/badge.svg)][pypi-upload]

# auditree-plant

The Auditree tool for adding external evidence.

## Introduction

Auditree `plant` is a command line tool that assists in adding evidence to an
evidence locker.  It provides a thoughtful way to add evidence to an
evidence locker by managing the evidence metadata so that checks and dependent fetchers
executed as part of the [Auditree compliance framework][auditree-framework] can apply
appropriate time to live validations.

## Prerequisites

- Supported for execution on OSX and LINUX.
- Supported for execution with Python 3.6 and above.

Python 3 must be installed, it can be downloaded from the [Python][python-dl]
site or installed using your package manager.

Python version can be checked with:

```sh
python --version
```

or

```sh
python3 --version
```

The `plant` tool is available for download from [PyPI](https://pypi.org/).

## Installation

It is best practice, but not mandatory, to run `plant` from a dedicated Python
virtual environment.  Assuming that you have the Python [virtualenv][virtual-env]
package already installed, you can create a virtual environment named `venv` by
executing `virtualenv venv` which will create a `venv` folder at the location of
where you executed the command.  Alternatively you can use the python `venv` module
to do the same.

```sh
python3 -m venv venv
```

Assuming that you have a virtual environment and that virtual environment is in
the current directory then to install a new instance of `plant`, activate
your virtual environment and use `pip` to install `plant` like so:

```sh
. ./venv/bin/activate
pip install auditree-plant
```

As we add new features to `plant` you will want to upgrade your `plant`
package.  To upgrade `plant` to the most recent version do:

```sh
. ./venv/bin/activate
pip install auditree-plant --upgrade
```

See [pip documentation][pip-docs] for additional options when using `pip`.

## Configuration

Since Auditree `plant` interacts with Git repositories, it requires Git remote
hosting service credentials in order to do its thing.  Auditree `plant` will by
default look for a `username` and `token` in a `~/.credentials` file.  You can
override the credentials file location by using the `--creds` option on a `plant`
CLI execution. Valid section headings include `github`, `github_enterprise`, `bitbucket`,
and `gitlab`.  Below is an example of the expected credentials entry.

```ini
[github]
username=your-gh-username
token=your-gh-token
```

## Execution

Auditree `plant` is a simple CLI that performs the function of adding evidence
to an evidence locker.  As such, it has two execution modes; a `push-remote` mode
and a `dry-run` mode.  Both modes will clone a git repository and place it into the
`$TMPDIR/plant` folder.  Both modes will also provide handy progress output as
`plant` processes the new evidence.  However, `push-remote` will push the changes
to the remote repository before removing the locally cloned copy whereas `dry-run`
will not.  When provided an absolute path to a local git repository using the
`--repo-path` option, `plant` will perform its plant-like duties as described
on the specified local git repository.  This can come in handy when looking to
chain your `plant` execution after a successful run of the compliance automation
fetchers and checks.

As most CLIs, Auditree `plant` comes with a help facility.

```sh
plant -h
```

```sh
plant push-remote -h
```

```sh
plant dry-run -h
```

### push-remote mode

Use the `push-remote` mode when you want your changes to be applied to the remote
evidence locker.  You can provide as many _evidence path_/_evidence detail_
key/value pairs as you need as part of the `--config` or as contents of your
`--config-file`.

```sh
plant push-remote https://github.com/org-foo/repo-bar --config '{"/absolute/path/to/my/evidence.ext":{"category":"foo"}}'
```

```sh
plant push-remote https://github.com/org-foo/repo-bar --config-file ./path/to/my/config_file.json
```

```sh
plant push-remote https://github.com/org-foo/repo-bar --repo-path $TMPDIR"compliance" --config-file ./path/to/my/config_file.json
```

### dry-run mode

Use the `dry-run` mode when you don't want your changes to be applied to the remote
evidence locker and are just interested in seeing what effect the execution will have
on your evidence locker before you commit to pushing your changes to the remote repository.
You can provide as many _evidence path_/_evidence detail_ key/value pairs as you
need as part of the `--config` or as contents of your `--config-file`.

```sh
plant dry-run https://github.com/org-foo/repo-bar --config '{"/absolute/path/to/my/evidence.ext":{"category":"foo"}}'
```

```sh
plant dry-run https://github.com/org-foo/repo-bar --config-file ./path/to/my/config_file.json
```

```sh
plant dry-run https://github.com/org-foo/repo-bar --repo-path $TMPDIR"compliance" --config-file ./path/to/my/config_file.json
```


[platform-badge]: https://img.shields.io/badge/platform-osx%20|%20linux-orange.svg
[python-badge]: https://img.shields.io/badge/python-v3.6+-blue.svg
[pre-commit-badge]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
[python-dl]: https://www.python.org/downloads/
[pre-commit]: https://github.com/pre-commit/pre-commit
[pip-docs]: https://pip.pypa.io/en/stable/reference/pip/
[virtual-env]: https://pypi.org/project/virtualenv/
[auditree-framework]: https://github.com/ComplianceAsCode/auditree-framework
[lint-test]: https://github.com/ComplianceAsCode/auditree-plant/actions?query=workflow%3A%22Test+python+code+%26+lint%22
[pypi-upload]: https://github.com/ComplianceAsCode/auditree-plant/actions?query=workflow%3A%22Upload+Python+Package%22
