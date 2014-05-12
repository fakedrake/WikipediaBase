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
    packages=['wikipediabase'],
    include_package_data=True,
    install_requires=[
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
