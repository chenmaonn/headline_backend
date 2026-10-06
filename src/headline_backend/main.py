"""程序入口"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import FastAPI

from src.headline_backend.core.logging.logging_config import logging_init

logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    print("开始启动")

    print("开始初始化日志")
    logging_init()

    logger.info("日志初始化完成")
    yield


app = FastAPI(lifespan=lifespan)
