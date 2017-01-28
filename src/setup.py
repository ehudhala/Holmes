import os

from setuptools import setup, find_packages

PROJECT_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README_FILE_NAME = os.path.join(PROJECT_BASE, 'README.md')


with open(README_FILE_NAME, 'rb') as readme_file:
    description = readme_file.read()


setup(name='holmes',
      version='0.1',
      short_description='Used for registering kids to Holmes Place lessons',
      long_description=description,
      packages=find_packages())