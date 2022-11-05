[![Python 3.7 | 3.8 | 3.9 | 3.10 | 3.11](https://img.shields.io/badge/Python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)](https://www.python.org/downloads)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Preocts/commented-configparser/main.svg)](https://results.pre-commit.ci/latest/github/Preocts/commented-configparser/main)
[![Python tests](https://github.com/Preocts/commented-configparser/actions/workflows/python-tests.yml/badge.svg?branch=main)](https://github.com/Preocts/commented-configparser/actions/workflows/python-tests.yml)

# commented-configparser

A custom ConfigParser class that preserves comments when writing loaded config out.

This library gives you a custom class of the standard library's `configparser.ConfigParger` which will preserve the comments of a loaded config file when writing that file back out.

---

## Install via pip

From pypi:

```bash
python -m pip install commented-configparser
```

From github:

```bash
python -m pip install commented-configparser@git+https://github.com/Preocts/commented-configparser@main
```

**Note:** Replace `main` with the desired tag or branch.  This can be placed in a `requirements.txt` file as well.

---

## Example use

```py
from commentedconfigparser import CommentedConfigParser

# Load the config like normal
config = CommentedConfigParser()
config.read("myconfig.ini")

# Use the config like normal
...

# Update the config like normal
...

# Save the config back to the file
with open("myconfig.ini", "w") as savefile:
    config.write(savefile)
```

## Results

We favor the line spacing choices of the `ConfigParser` class so the input format may not be preserved completely. However, the comments will be preserved.

### Before

```ini
# Welcome to our config
[DEFAULT]
# This value has some meaning to someone
foo=bar
# Make sure to add this when you need it
trace=false
logging=true
; This is a comment as well

    # so we need to track all of them

	; and many could be between things
[NEW SECTION]
# Another comment
multi-line=
	value01
	value02
	value03
closing=0
# Trailing comment

```

### After

```ini
# Welcome to our config
[DEFAULT]
# This value has some meaning to someone
foo=bar
# Make sure to add this when you need it
trace=false
logging=true
; This is a comment as well
    # so we need to track all of them
	; and many could be between things

[NEW SECTION]
# Another comment
multi-line=
	value01
	value02
	value03
closing=0
# Trailing comment

```

---

# Local developer installation

It is **strongly** recommended to use a virtual environment
([`venv`](https://docs.python.org/3/library/venv.html)) when working with python
projects. Leveraging a `venv` will ensure the installed dependency files will
not impact other python projects or any system dependencies.

The following steps outline how to install this repo for local development. See
the [CONTRIBUTING.md](CONTRIBUTING.md) file in the repo root for information on
contributing to the repo.

**Windows users**: Depending on your python install you will use `py` in place
of `python` to create the `venv`.

**Linux/Mac users**: Replace `python`, if needed, with the appropriate call to
the desired version while creating the `venv`. (e.g. `python3` or `python3.8`)

**All users**: Once inside an active `venv` all systems should allow the use of
`python` for command line instructions. This will ensure you are using the
`venv`'s python and not the system level python.

---

## Installation steps

Clone this repo and enter root directory of repo:

```console
$ git clone https://github.com/Preocts/commented-configparser
$ cd commented-configparser
```

Create the `venv`:

```console
$ python -m venv venv
```

Activate the `venv`:

```console
# Linux/Mac
$ . venv/bin/activate

# Windows
$ venv\Scripts\activate
```

The command prompt should now have a `(venv)` prefix on it. `python` will now
call the version of the interpreter used to create the `venv`

Install editable library and development requirements:

```console
# Update pip and tools
$ python -m pip install --upgrade pip

# Install editable version of library
$ python -m pip install --editable .[dev]
```

Install pre-commit [(see below for details)](#pre-commit):

```console
$ pre-commit install
```

---

## Misc Steps

Run pre-commit on all files:

```console
$ pre-commit run --all-files
```

Run tests:

```console
$ tox [-r] [-e py3x]
```

Build dist:

```console
$ python -m pip install --upgrade build

$ python -m build
```

To deactivate (exit) the `venv`:

```console
$ deactivate
```
---

## Note on flake8:

`flake8` is included in the `requirements-dev.txt` of the project. However it
disagrees with `black`, the formatter of choice, on max-line-length and two
general linting errors. `.pre-commit-config.yaml` is already configured to
ignore these. `flake8` doesn't support `pyproject.toml` so be sure to add the
following to the editor of choice as needed.

```ini
--ignore=W503,E203
--max-line-length=88
```

---

## [pre-commit](https://pre-commit.com)

> A framework for managing and maintaining multi-language pre-commit hooks.

This repo is setup with a `.pre-commit-config.yaml` with the expectation that
any code submitted for review already passes all selected pre-commit checks.
`pre-commit` is installed with the development requirements and runs seemlessly
with `git` hooks.

---

## Makefile

This repo has a Makefile with some quality of life scripts if the system
supports `make`.  Please note there are no checks for an active `venv` in the
Makefile.

| PHONY         | Description                                                                |
| ------------- | -------------------------------------------------------------------------- |
| `init`        | Update pip to newest version                                               |
| `install`     | install the project                                                        |
| `install-dev` | install development/test requirements and project as editable install      |
| `upgrade-dev` | update all dependencies, regenerate requirements.txt (disabled by default) |
| `build-dist`  | Build source distribution and wheel distribution                           |
| `clean`       | Deletes build, tox, coverage, pytest, mypy, cache, and pyc artifacts       |
