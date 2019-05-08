#  Drakkar-Software OctoBot-Tentacles-Manager-Launcher
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
import os

from setuptools import setup, find_packages

from tentacles_manager import PROJECT_NAME, VERSION


def find_package_data(path):
    return (path, [os.path.join(dirpath, filename)
                   for dirpath, dirnames, filenames in os.walk(path)
                   for filename in
                   [file for file in filenames if not file.endswith(".py") and not file.endswith(".pyc")]])


PACKAGES = find_packages()

PACKAGES_DATA = [find_package_data("tentacles_manager/tentacle_creator/templates")]

# long description from README file
with open('README.md', encoding='utf-8') as f:
    DESCRIPTION = f.read()

REQUIRED = open('requirements.txt').read()
REQUIRES_PYTHON = '>=3.6'

setup(
    name=PROJECT_NAME,
    version=VERSION,
    url='https://github.com/Drakkar-Software/OctoBot-Tentacles-Manager',
    license='LGPL-3.0',
    author='Drakkar-Software',
    author_email='drakkar-software@protonmail.com',
    description='OctoBot project module installer',
    packages=PACKAGES,
    long_description=DESCRIPTION,
    install_requires=REQUIRED,
    tests_require=["pytest"],
    test_suite="tests",
    zip_safe=False,
    data_files=PACKAGES_DATA,
    python_requires=REQUIRES_PYTHON,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3.6',
    ],
)
