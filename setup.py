# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='bonspy',
    version='1.1',
    description='Library that converts bidding trees to the AppNexus Bonsai language.',
    author='Alexander Volkmann, Georg Walther',
    author_email='contact@markovian.com',
    packages=['bonspy'],
    package_dir={'bonspy': 'bonspy'},
    url='https://github.com/markovianhq/bonspy',
    download_url='https://github.com/markovianhq/bonspy/tarball/master',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3'
    ]
)
