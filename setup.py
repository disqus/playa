#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

tests_require = [
    'nose',
    'unittest2',
]

setup(
    name='playa',
    version='0.1',
    author='David Cramer',
    author_email='dcramer@gmail.com',
    url='http://github.com/dcramer/playa',
    description = 'Audio Playing Service',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'Flask',
        # good luck installing these
        'pymad==0.6', # http://spacepants.org/src/pymad/download/pymad-0.6.tar.gz
        'pyaudio',
        'mutagen',
        # python-daemon and eventlet are required to run the Sentry indepenent webserver
        'python-daemon>=1.6',
        'eventlet>=0.9.15',
        # uuid ensures compatibility with older versions of Python
        'uuid',
    ],
    dependency_links=[
    ],
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='nose.main',
    include_package_data=True,
    entry_points = {
        'console_scripts': [
            'playa = playa.runner:main',
        ],
    },
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
