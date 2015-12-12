*Under active development. Go no further unless you know what you are
 doing.*

# wikipediabase

[![Build Status](https://travis-ci.org/infolab-csail/WikipediaBase.svg?branch=master)](https://travis-ci.org/infolab-csail/WikipediaBase)
[![Stories in Ready](https://badge.waffle.io/infolab-csail/WikipediaBase.svg?label=ready&title=Ready)](http://waffle.io/infolab-csail/WikipediaBase)
[![Coverage Status](https://coveralls.io/repos/infolab-csail/WikipediaBase/badge.svg?branch=master&service=github)](https://coveralls.io/github/infolab-csail/WikipediaBase?branch=master)

## Overview

Wikipedia backend interface for
[InfoLab's START](http://start.mit.edu). It answers s-expression
queries via Telnet.

## Documentation

[API documentation](http://wikipediabase.rtfd.org)

## Installing
Install `pip` and `redis-server` if not installed:

    apt-get install python-setuptools redis-server

> Caution: Until wikipedibase is deployed on START installing it for non-testing purposes is not something one is supposed to do.

Install `wikipediabase`:

    python setup.py install

## Setting up the backend

1. Configure the backend. The scripts checks that Postgres and Redis are running, and creates the necessary tables.

   ```
   ./scripts/configure_db.py
   ```

   If Postgres throws `ERROR: new encoding (UTF8) is incompatible with the encoding of the template database (SQL_ASCII)`, follow [these](https://gist.github.com/ffmike/877447) instructions.

1. Download the latest Wikipedia [dump](http://dumps.wikimedia.org/enwiki/).

1. Create the backend. This step takes about 10 hours.

   ```
   bzcat /path/to/enwiki-YYYYMMDD-pages-articles.xml.bz2 | ./scripts/create_db.py
   ```

1. Generate symbols and synonyms (optional). This step takes about 40 hours.

   ```
   ./scripts/generate_symbols_and_synonyms.py
   ```

   Install [Git LFS](https://git-lfs.github.com/) and commit the changes to files in `data/`.

## Testing

Install development requirements (do this after every 'git pull' in
case there are new requirements):

    python setup.py develop

Tests can then be run with:

    python setup.py test

_Note: tests assume that you have set up the backend. To fetch from wikipedia.org instead of reading from the database, set the env variable `WIKIPEDIABASE_FORCE_LIVE=true`. This is strongly discouraged if you plan to use or contribute to WikipediaBase, as performance will be slow._

## API documentation

Generate the documentation with:

    cd docs && PYTHONPATH=.. make singlehtml
