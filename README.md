# wikipediabasepy

[![Build Status](https://secure.travis-ci.org/fakedrake/wikipediabasepy.png)](http://travis-ci.org/fakedrake/wikipediabasepy)
[![Stories in Ready](https://badge.waffle.io/fakedrake/wikipediabasepy.png?label=ready)](https://waffle.io/fakedrake/wikipediabasepy) [![pypi version](https://badge.fury.io/py/wikipediabasepy.png)](http://badge.fury.io/py/wikipediabasepy)
[![# of downloads](https://pypip.in/d/wikipediabasepy/badge.png)](https://crate.io/packages/wikipediabasepy?version=latest)
[![code coverage](https://coveralls.io/repos/fakedrake/wikipediabasepy/badge.png?branch=master)](https://coveralls.io/r/fakedrake/wikipediabasepy?branch=master)

## Overview

Wikipedia backend interface for start.mit.edu

* features
* and stuff 

## Usage

Install `wikipediabasepy`:

    pip install wikipediabasepy

## Documentation

[API Documentation](http://wikipediabasepy.rtfd.org)

## Testing

Install development requirements:

    pip install -r requirements.txt

Tests can then be run with:

    nosetests

Lint the project with:

    flake8 wikipediabasepy tests

## API documentation

Generate the documentation with:

    cd docs && PYTHONPATH=.. make singlehtml

To monitor changes to Python files and execute flake8 and nosetests
automatically, execute the following from the root project directory:

    stir