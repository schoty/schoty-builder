# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from schoty._version import __version__


setup(name='schoty',
      version=__version__,
      description='A monorepo builder and synchronisation engine',
      author='Roman Yurchak',
      packages=find_packages(),
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'schoty = schoty.__main__:main'
          ]
      },
      python_requires='>=3.6')
