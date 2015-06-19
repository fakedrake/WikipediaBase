import re
import multiprocessing
from setuptools import setup
from pip.req import parse_requirements
from pip.download import PipSession

install_reqs = parse_requirements('requirements.txt',
                                  session=PipSession())
reqs = [str(ir.req) for ir in install_reqs]
req_links = [str(req_line.url) for req_line in install_reqs]
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
    install_requires=reqs,
    dependency_links=reqlinks,
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
