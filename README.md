[![Python 3.8 | 3.9 | 3.10 | 3.11 | 3.12](https://img.shields.io/badge/Python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/downloads)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Preocts/commented-configparser/main.svg)](https://results.pre-commit.ci/latest/github/Preocts/commented-configparser/main)
[![Python tests](https://github.com/Preocts/commented-configparser/actions/workflows/python-tests.yml/badge.svg?branch=main)](https://github.com/Preocts/commented-configparser/actions/workflows/python-tests.yml)

# commented-configparser

A custom ConfigParser class that preserves comments and option casing when writing loaded config out.

This library gives you a custom class of the standard library's `configparser.ConfigParger` which will preserve the comments of a loaded config file when writing that file back out.

---

## Install via pip

From pypi:

```bash
python -m pip install commented-configparser
```

From github:

```bash
python -m pip install commented-configparser@git+https://github.com/Preocts/commented-configparser@x.x.x
```

**Note:** Replace `x.x.x` with the desired tag or branch.

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
foo = bar
# Make sure to add this when you need it
trace = false
logging = true
; This is a comment as well
# so we need to track all of them
; and many could be between things

[NEW SECTION]
# Another comment
multi-line =
	value01
	value02
	value03
closing = 0
# Trailing comment

```

---

# Local developer installation

The following steps outline how to install this repo for local development.

## Prerequisites

### Clone repo

```console
git clone https://github.com/Precots/commented-configparser

cd commented-configparser
```

### Virtual Environment

Use a ([`venv`](https://docs.python.org/3/library/venv.html)), or equivalent,
when working with python projects. Leveraging a `venv` will ensure the installed
dependency files will not impact other python projects or any system
dependencies.

**Windows users**: Depending on your python install you will use `py` in place
of `python` to create the `venv`.

**Linux/Mac users**: Replace `python`, if needed, with the appropriate call to
the desired version while creating the `venv`. (e.g. `python3` or `python3.8`)

**All users**: Once inside an active `venv` all systems should allow the use of
`python` for command line instructions. This will ensure you are using the
`venv`'s python and not the system level python.

### Create the `venv`:

```console
python -m venv venv
```

Activate the `venv`:

```console
# Linux/Mac
. venv/bin/activate

# Windows
venv\Scripts\activate
```

The command prompt should now have a `(venv)` prefix on it. `python` will now
call the version of the interpreter used to create the `venv`

To deactivate (exit) the `venv`:

```console
deactivate
```

---

## Developer Installation Steps

### Install editable library and development requirements

```console
python -m pip install --editable .[dev,test]
```

### Install pre-commit [(see below for details)](#pre-commit)

```console
pre-commit install
```

### Install with nox

If you have `nox` installed with `pipx` or in the current venv you can use the
following session. This is an alternative to the two steps above.

```console
nox -s install
```

---

## Pre-commit and nox tools

### Run pre-commit on all files

```console
pre-commit run --all-files
```

### Run tests with coverage (quick)

```console
nox -e coverage
```

### Run tests (slow)

```console
nox
```

### Build dist

```console
nox -e build
```

---

## Updating dependencies

New dependencys can be added to the `requirements-*.in` file. It is recommended
to only use pins when specific versions or upgrades beyond a certain version are
to be avoided. Otherwise, allow `pip-compile` to manage the pins in the
generated `requirements-*.txt` files.

Once updated following the steps below, the package can be installed if needed.

### Update the generated files with changes

```console
nox -e update
```

### Upgrade all generated dependencies

```console
nox -e upgrade
```

---

## [pre-commit](https://pre-commit.com)

> A framework for managing and maintaining multi-language pre-commit hooks.

This repo is setup with a `.pre-commit-config.yaml` with the expectation that
any code submitted for review already passes all selected pre-commit checks.

---

## Error: File "setup.py" not found

Update `pip` to at least version 22.3.1
