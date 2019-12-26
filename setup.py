#!/usr/bin/env python

from distutils.core import setup

import django_pglocks

def get_long_description():
    """
    Return the contents of the README file.
    """
    try:
        return open('README.rst').read()
    except:
        pass  # Required to install using pip (won't have README then)

setup(
    name = 'django-pglocks',
    version = django_pglocks.__version__,
    description = "django_pglocks provides useful context managers for advisory locks for PostgreSQL.",
    long_description = get_long_description(),
    author = "Christophe Pettus",
    author_email = "xof@thebuild.com",
    license = "MIT",
    url = "https://github.com/Xof/django-pglocks",
    install_requires = ['six>=1.0.0'],
    packages = [
        'django_pglocks',
    ],
    package_data = {
        'facetools': ['templates/facetools/facebook_redirect.html'],
    },
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ]
)
