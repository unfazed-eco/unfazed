import os
import sys
import typing as t

import pytest
from pytest import Item
from pytest_asyncio import is_async_test
from unfazed.core import Unfazed


# dont need decorate test functions with pytest.mark.asyncio
def pytest_collection_modifyitems(items: t.List[Item]) -> None:
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)


# create a global unfazed
# use this fixture in your test functions
@pytest.fixture(autouse=True)
async def unfazed() -> t.AsyncGenerator[Unfazed, None]:
    root_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(root_path)
    os.environ.setdefault("UNFAZED_SETTINGS_MODULE", "entry.settings")
    unfazed = Unfazed()
    await unfazed.setup()

    yield unfazed
