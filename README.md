[![Python 3.9 | 3.10 | 3.11 | 3.12 | 3.13 | 3.14](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](https://www.python.org/downloads)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Preocts/commented-configparser/main.svg)](https://results.pre-commit.ci/latest/github/Preocts/commented-configparser/main)
[![Python tests](https://github.com/Preocts/commented-configparser/actions/workflows/python-tests.yml/badge.svg?branch=main)](https://github.com/Preocts/commented-configparser/actions/workflows/python-tests.yml)

# commented-configparser

- [Contributing Guide and Developer Setup Guide](./CONTRIBUTING.md)
- [License: MIT](./LICENSE)

---

A custom ConfigParser class that preserves comments and most formatting when
writing loaded config out.

This library gives you a custom class of the standard library's
`configparser.ConfigParger` which will preserve the comments of a loaded config
file when writing that file back out.

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

There is the attempt to retain the original format. Known formats that will not
be preserved:

1. Indents will not be preserved outside of multi-line values
2. Spacing around assignments will be normalized.

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
multiLine=
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
multiLine =
	value01
	value02
	value03
closing = 0
# Trailing comment
```
