import re
from setuptools import setup

init_py = open('wikipediabase/__init__.py').read()
metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", init_py))
metadata['doc'] = re.findall('"""(.+)"""', init_py)[0]

setup(
    name='wikipediabase',
    version=metadata['version'],
    description=metadata['doc'],
    author=metadata['author'],
    author_email=metadata['email'],
    url=metadata['url'],
    packages=[
        'wikipediabase',
        'wikipediabase.resolvers',
    ],
    include_package_data=True,
    install_requires=[
        'beautifulsoup4',
        'docopt',
        'edn_format',
        'flake8 < 3.0.0',
        'fuzzywuzzy',
        'hiredis',
        'lxml',
        'overlay-parse',
        'redis',
        'requests',
        'sqlitedict',
        'unidecode',
        'unittest2 < 1.0.0',
    ],
    dependency_links=[
        'git+https://github.com/fakedrake/overlay_parse#egg=overlay-parse',
    ],
    tests_require=[
        'nose>=1.0',
        'sqlitedict'
    ],
    entry_points={
        'console_scripts': [
            'wikipediabase = wikipediabase.cli:main',
        ],
    },
    test_suite='nose.collector',
    license=open('LICENSE').read(),
)
