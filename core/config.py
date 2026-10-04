import logging
from functools import cached_property
from pathlib import Path
from typing import Annotated, Literal

from pydantic import AfterValidator, Field
from pydantic_core import PydanticCustomError
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_PATH = Path(__file__).resolve().parent.parent  # 避免不同工作目录导致位置不同

ENV_FILE_PATH = PROJECT_PATH / ".env"


def get_abs_str_path(p: str) -> Path:
    """返回path的绝对路径

    Args:
        p (str): 需要转换的字符串

    Returns:
        Path: 转换的绝对路径
    """
    path = Path(p)

    if not path.is_absolute():
        path = PROJECT_PATH / path  # 通过项目路径转换为绝对路径
        path = path.resolve()

    return path


def normalize_dir(v: str) -> str:
    """规范化目录路径， 不检查是否存在

    Args:
        v (str): 需要规范化的字符串

    Returns:
        str: 规范化的路径字符串
    """
    path = get_abs_str_path(v)

    if not path.is_dir():
        raise PydanticCustomError(
            "invalid_dir",
            "不是有效的目录路径: {path}",
            {"path": str(path)},
        )
    return str(path)


def normalize_file(v: str) -> str:
    """规范化文件路径， 不检查是否存在

    Args:
        v (str): 需要规范化的字符串

    Returns:
        str: 规范化的路径字符串
    """
    path = get_abs_str_path(v)

    if not path.is_file():
        raise PydanticCustomError(
            "invalid_file",
            "不是有效的文件路径: {path}",
            {"path": str(path)},
        )
    return str(path)


def require_existing_dir(v: str) -> str:
    """规范化目录路径， 检查是否存在

    Args:
        v (str): 需要规范化的字符串

    Returns:
        str: 规范化的路径字符串
    """
    path = Path(normalize_dir(v))

    if not path.exists():
        raise PydanticCustomError(
            "file_not_found",
            "目录不不存在: {path}",
            {"path": str(path)},
        )

    return str(path)


def require_existing_file(v: str) -> str:
    """规范化文件路径， 检查是否存在

    Args:
        v (str): 需要规范化的字符串

    Returns:
        str: 规范化的路径字符串
    """
    path = Path(normalize_dir(v))

    if not path.exists():
        raise PydanticCustomError(
            "file_not_found",
            "文件不存在: {path}",
            {"path": str(path)},
        )

    return str(path)


DirPath = Annotated[str, AfterValidator(normalize_dir)]
FilePath = Annotated[str, AfterValidator(normalize_file)]
ExistingDir = Annotated[str, AfterValidator(require_existing_dir)]
ExistingFile = Annotated[str, AfterValidator(require_existing_file)]


class Setting(BaseSettings):
    """用于读取环境变量"""

    IS_PRODUCTION: bool = True

    PRINT_CONSOLE_LOG_LEVEL: Literal["DEBUG", "INFO", "WARING", "ERRO", "CRITICAL"] = (
        "INFO"
    )
    PRINT_CONSOLE_STREAM: str = "ext://sys.stdout"

    PRINT_FILE_LOG_LEVEL: Literal["DEBUG", "INFO", "WARING", "ERRO", "CRITICAL"] = (
        "INFO"
    )

    PRINT_FILE_LOG_ENCODING: str = "utf-8"
    PRINT_FILE_LOG_PATH: DirPath = "./logs"
    PRINT_FILE_LOG_WHEN: Literal["S", "M", "H", "D", "W", "midnight"] = "midnight"
    PRINT_FILE_LOG_INTERVAL: Annotated[int, Field(ge=1)] = 1
    PRINT_FILE_LOG_BACKUPCOUNT: Annotated[int, Field(ge=1)] = 30

    @cached_property
    def get_console_loglevel(self) -> int:
        """返回console log的等级

        Returns:
            int: 日志等级
        """
        return getattr(logging, self.PRINT_CONSOLE_LOG_LEVEL)

    @cached_property
    def get_file_loglevel(self) -> int:
        """返回file log的等级

        Returns:
            int: 日志等级
        """
        return getattr(logging, self.PRINT_FILE_LOG_LEVEL)

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH, extra="forbid", case_sensitive=False
    )


settings = Setting()
