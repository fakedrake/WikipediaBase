import re
import multiprocessing
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
    packages=['wikipediabase',
              'tests'],
    include_package_data=True,
    install_requires=[
        'edn_format',
        'changes < 1.0.0',
        'coverage < 4.0.0',
        'docopt',
        'flake8 < 3.0.0',
        'mock < 2.0.0',
        'nose < 2.0.0',
        'python-coveralls < 3.0.0',
        'sphinx-bootstrap-theme < 1.0.0',
        'testtube < 1.0.0',
        'travis-solo < 1.0.0',
        'unittest2 < 1.0.0',
        'overlay-parse',
        'lxml',
        'dataset'
    ],
    dependency_links=[
        'git+https://github.com/fakedrake/overlay_parse#egg=overlay-parse',
    ],
    tests_require=[
        'nose>=1.0',
    ],
    entry_points={
        'console_scripts': [
            'wikipediabase = wikipediabase.cli:main',
        ],
    },
    test_suite='nose.collector',
    license=open('LICENSE').read(),
)
