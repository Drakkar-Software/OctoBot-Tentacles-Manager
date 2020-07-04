#  Drakkar-Software OctoBot-Tentacles-Manager
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
import asyncio
from os import scandir, remove, getenv, getcwd, chdir
from os.path import exists, join
from shutil import rmtree
from setuptools import sandbox

from octobot_tentacles_manager.constants import TENTACLE_METADATA, COMPILED_TENTACLES_TO_REMOVE_ELEMENTS, \
    COMPILED_TENTACLES_TO_KEEP_ELEMENTS, CYTHON_PXD_HEADER, PYTHON_EXT, CYTHON_EXT, SETUP_FILE, PYTHON_INIT_FILE, \
    TENTACLE_TESTS, COMPILED_TENTACLES_TO_REMOVE_FOLDERS
from octobot_tentacles_manager.util.file_util import find_or_create


async def cythonize_and_compile_tentacles(directory):
    for element in scandir(directory):
        if element.name == TENTACLE_METADATA:
            # this folder is a tentacle: cythonize
            # remove test folder
            test_folder = join(directory, TENTACLE_TESTS)
            if exists(test_folder):
                rmtree(test_folder)
            await _cythonize_tentacle(directory)
            _compile_tentacle(directory)
            _clean_up_compiled_tentacle(directory)
            break
        elif element.is_dir():
            await cythonize_and_compile_tentacles(element)


async def _cythonize_tentacle(directory):
    # add missing .pxd files in directory and sub-directories
    # do not compile test files
    await _ensure_cython_header_files(directory)
    # update files
    if getenv('PACKAGER_UPDATE_FILES'):
        _update_files(directory)
    # add missing setup.py
    if not exists(join(directory, SETUP_FILE)):
        await _create_setup_file(directory)


async def _ensure_cython_header_files(directory):
    files = []
    directories = []
    for element in scandir(directory):
        if element.is_file():
            files.append(element.name)
        elif element.is_dir() and element.name:
            directories.append(element)
    coros = []
    for element in files:
        element_simple_name = element.split(".")[0]
        header_file = f"{element_simple_name}{CYTHON_EXT}"
        if element.endswith(PYTHON_EXT) and header_file not in files:
            # this python file has no existing header file: create default one
            coros.append(find_or_create(join(directory, header_file),
                                        is_directory=False, file_content=CYTHON_PXD_HEADER))
    for directory in directories:
        coros.append(_ensure_cython_header_files(directory))
    await asyncio.gather(*coros)


async def _create_setup_file(directory):
    package_list = _find_packages(directory)
    await find_or_create(join(directory, SETUP_FILE), is_directory=False,
                         file_content=_get_setup_file_content(package_list))


def _find_packages(directory, parent_path=""):
    package_list = []
    for element in scandir(directory):
        if element.name.endswith(PYTHON_EXT) and element.name != PYTHON_INIT_FILE:
            package_list.append(f"{parent_path}{element.name.split(PYTHON_EXT)[0]}")
        elif element.is_dir():
            package_list += _find_packages(element, parent_path=f"{parent_path}{element.name}.")
    return package_list


def _update_files(directory):
    # for later uses
    pass


def _compile_tentacle(directory):
    previous_dir = getcwd()
    chdir(directory)
    sandbox.run_setup('setup.py', ['build_ext', '-i'])
    chdir(previous_dir)


def _clean_up_compiled_tentacle(directory):
    for element in scandir(directory):
        element_ext = element.name.split(".")[-1]
        if element.name in COMPILED_TENTACLES_TO_REMOVE_FOLDERS or \
                (f".{element_ext}" in COMPILED_TENTACLES_TO_REMOVE_ELEMENTS
                 and element not in COMPILED_TENTACLES_TO_KEEP_ELEMENTS
                 and element.is_file()):
            if element.is_dir():
                rmtree(element)
            elif element.is_file():
                remove(element)
        elif element.is_dir():
            _clean_up_compiled_tentacle(element)


def _get_setup_file_content(package_list):
    return f"""
import os

from setuptools import dist

dist.Distribution().fetch_build_eggs(['Cython'])

try:
    from Cython.Distutils import build_ext
    from Cython.Build import cythonize
except ImportError:
    # create closure for deferred import
    def cythonize(*args, **kwargs):
        from Cython.Build import cythonize
        return cythonize(*args, **kwargs)

    def build_ext(*args, **kwargs):
        from Cython.Distutils import build_ext
        return build_ext(*args, **kwargs)

from setuptools import setup, Extension

packages_list = {package_list}

ext_modules = [
    Extension(package, [f"{{package.replace('.', '/')}}.py"])
    for package in packages_list]

setup(
    ext_modules=cythonize(ext_modules),
)
"""
