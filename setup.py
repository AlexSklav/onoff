#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from setuptools import setup
from setuptools.command.build_py import build_py

import onoff

setup(
    name="onoff",
    cmdclass={'build_py': build_py},
    version=onoff.__version__,
    description="A universal mixin to add on(), off(), and trigger() style event handling to any Python class.",
    author=onoff.__author__,
    author_email="daniel.mcdougall@liftoffsoftware.com",
    url="https://github.com/liftoff/onoff",
    license="Apache 2.0",
    py_modules=["onoff"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries",
        "Operating System :: OS Independent",
    ]
)
