from setuptools import setup, find_packages
from codecs import open
from os import path

__version__ = '0.1'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]

setup(
    name='spoticonnect',
    version=__version__,
    description='Python package to control Spotify and Spotify Connect without requiring spotify locally installed',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/aerospeace/spoticonnect',
    download_url='https://github.com/aerospeace/spoticonnect/tarball/' + __version__,
    license='BSD',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.5',
    keywords='',
    packages=find_packages(exclude=['docs', 'tests*']),
    entry_points={"console_scripts": ["spoticonnect = spoticonnect.main:main"]},
    include_package_data=True,
    author='Hicham Tahiri',
    install_requires=install_requires,
    dependency_links=dependency_links,
)
