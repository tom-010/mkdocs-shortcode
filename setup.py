import os
from setuptools import setup, find_packages
from distutils.core import setup

setup(
    name='mkdocs_shortcode',
    version='0.1.0',
    author='Thomas Deniffel',
    author_email='tdeniffel@gmail.com',
    packages=['mkdocs_shortcode'],
    license='LICENSE.txt',
    description='Add Shortcodes',
    python_requires='>=3.6',
    entry_points={
        'mkdocs.plugins': [
            'shortcode = mkdocs_shortcode.plugin:ShortcodePlugin',
        ]
    }
)