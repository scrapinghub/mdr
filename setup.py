import numpy

from setuptools import setup, Extension

ext_modules = [Extension('mdr._tree',
    sources=['mdr/_tree.c'],
    include_dirs = [numpy.get_include()],
)]

setup(name='mdr',
      version='0.0.0',
      description="python library to detect and extract listing data from HTML page",
      long_description="",
      author="Terry Peng",
      author_email="pengtaoo@gmail.com",
      packages=['mdr'],
      ext_modules=ext_modules
)