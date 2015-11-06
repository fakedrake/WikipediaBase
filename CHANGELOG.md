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

The above was achieved by using a reference based configuration
system.

Hopefully this change will make experimentation with the system much
easier and will make the code more scalable and understandable.

## Separation of concerns

Certain parts of the code had less than ideal structure. That was the
case mostly when it came to string manipulation. For that reason
web_strings.py was created to accomodate all low level data
manipulation.

## Misc

- Object caching is (hopefully) not insane anymore.
- TODO: Enchanted classes are now called StartTypes.
- TODO: file names (like infobox_scraper) match the most interesting
  class in them
- Test net activity is cached.
