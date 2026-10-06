"""全局测试夹具"""

import pytest


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    """个测试会话开始前执行一次"""
