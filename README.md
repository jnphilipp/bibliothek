# bibliothek

Commandline libary tool with a web interface.

[![Tests](https://github.com/jnphilipp/backup/actions/workflows/tests.yml/badge.svg)](https://github.com/jnphilipp/backup/actions/workflows/tests.yml)

## Requirements
* Python 3.7 or newer
* python-django
* python-bibtexparser
* python-pillow


## Install

* from Source: ```make install```
* deb-Package: ```make deb```
* [AUR](https://aur.archlinux.org/packages/bibliothek)

To enable systemd service on startup:

```
systemctl --user enable ledger.service
```

## Usage

For options see `$ bibliothek -h`.
