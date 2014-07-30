from setuptools import setup, Extension
import numpy

ext_modules = [Extension('mdr._tree',
    sources=['mdr/_tree.c'],
    include_dirs = [numpy.get_include()],
)]

setup(name='mdr',
      version='0.0.1',
      description="python library to detect and extract listing data from HTML page",
      long_description="",
      author="Terry Peng",
      author_email="pengtaoo@gmail.com",
      url='https://github.com/tpeng/mdr',
      license='MIT',
      packages=['mdr'],
      ext_modules=ext_modules,
      install_requires=['lxml', 'scipy>=0.7.0', 'numpy>=1.5.1']
)