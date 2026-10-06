"""集成测试夹具"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from headline_backend.infrastructure.db.base import Base

DB_CONNECT_STR = "sqlite+aiosqlite:///./tests/integration/headline_backend_tests.db"  # 数据库连接字符串


@pytest.fixture(scope="session")
def create_db_session():
    """创建测试数据库连接"""
    db_engine = create_engine(DB_CONNECT_STR)
    db_session = sessionmaker(db_engine)
