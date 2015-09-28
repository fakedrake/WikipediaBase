# [Changelog](https://github.com/fakedrake/wikipediabase/releases)

## 1.2

There was some pretty intrusive refactoring in this version. The
issues addresed were:

## Configuration

There was no good way of configuring without hardcoding the
changes. Since wikipedia-base is (currently) used mainly as a library
for multiple different purposes, it is required that each application
can use different key-value persistence method or destination,
wikipedia mirror, string encoding method, usage of mediawiki API or
plain html etc. It should also be possible to extend WikipediaBase
without actually messing with the core source. For example it might be
useful to create a new Fetcher from scratch or add new classifiers and
plug them into the system.
