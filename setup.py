#!/usr/bin/env python

from setuptools import setup

setup(name='stn',
      packages=['stn', 'stn.config', 'stn.exceptions', 'stn.methods', 'stn.pstn', 'stn.stnu', 'stn.utils'],
      version='0.2.0',
      install_requires=[
            'numpy',
            'networkx',
            'PuLP',
            'scipy',
            'pyYAML'
      ],
      description='Includes simple temporal_networks like STN, STNU and PSTN',
      author='Angela Enriquez Gomez',
      author_email='angela.enriquez@smail.inf.h-brs.de',
      package_dir={'': '.'}
      )
