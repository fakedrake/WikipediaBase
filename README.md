# wikipediabase

[![Build Status](https://secure.travis-ci.org/fakedrake/WikipediaBase.png)](http://travis-ci.org/fakedrake/WikipediaBase)
[![Stories in Ready](https://badge.waffle.io/fakedrake/wikipediabase.png?label=ready)](https://waffle.io/fakedrake/wikipediabase) [![pypi version](https://badge.fury.io/py/wikipediabase.png)](http://badge.fury.io/py/wikipediabase)
[![# of downloads](https://pypip.in/d/wikipediabase/badge.png)](https://crate.io/packages/wikipediabase?version=latest)
[![code coverage](https://coveralls.io/repos/fakedrake/wikipediabase/badge.png?branch=master)](https://coveralls.io/r/fakedrake/wikipediabase?branch=master)

## Overview

Wikipedia backend interface for
[InfoLab's START](http://start.mit.edu). It an answer s-expression
queries via Telnet.

## Usage

Install `pip` if not installed:

    apt-get install python-setuptools

Install `wikipediabase`:

    pip install wikipediabase

## Documentation

[API Documentation](http://wikipediabase.rtfd.org)

## Testing

Install development requirements (do this after every 'git pull' in
case there are new requirements):

    pip install -r requirements.txt

Tests can then be run with:

    python setup.py test

## API documentation

Generate the documentation with:

    cd docs && PYTHONPATH=.. make singlehtml
