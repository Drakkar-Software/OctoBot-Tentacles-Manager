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
import pytest
import sys
import asyncio

import octobot_commons.asyncio_tools as asyncio_tools


@pytest.yield_fixture
def event_loop():
    # re-configure async loop each time this fixture is called
    _configure_async_test_loop()
    loop = asyncio.new_event_loop()
    # use ErrorContainer to catch otherwise hidden exceptions occurring in async scheduled tasks
    error_container = asyncio_tools.ErrorContainer()
    loop.set_exception_handler(error_container.exception_handler)
    yield loop
    # will fail if exceptions have been silently raised
    loop.run_until_complete(error_container.check())
    loop.close()


def _configure_async_test_loop():
    if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
        # use WindowsSelectorEventLoopPolicy to avoid aiohttp connexion close warnings
        # https://github.com/encode/httpx/issues/914#issuecomment-622586610
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# set default values for async loop
_configure_async_test_loop()
