"""解析环境变量配置"""

import logging
from functools import cached_property
from pathlib import Path
from typing import Annotated, Literal

from pydantic import AfterValidator, Field, field_validator
from pydantic_core import PydanticCustomError
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent
)  # 避免不同工作目录导致位置不同

ENV_FILE_PATH = PROJECT_PATH / ".env"


class PathCheck:
    """用于检测目录"""

    @staticmethod
    def _get_abs_str_path(p: str) -> Path:
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

    @staticmethod
    def _normalize_dir(v: str) -> str:
        """规范化目录路径， 不检查是否存在

        Args:
            v (str): 需要规范化的字符串

        Returns:
            str: 规范化的路径字符串
        """
        path = PathCheck._get_abs_str_path(v)

        if not path.is_dir():
            raise PydanticCustomError(
                "invalid_dir",
                "不是有效的目录路径: {path}",
                {"path": str(path)},
            )
        return str(path)

    @staticmethod
    def _normalize_file(v: str) -> str:
        """规范化文件路径， 不检查是否存在

        Args:
            v (str): 需要规范化的字符串

        Returns:
            str: 规范化的路径字符串
        """
        path = PathCheck._get_abs_str_path(v)

        if not path.is_file():
            raise PydanticCustomError(
                "invalid_file",
                "不是有效的文件路径: {path}",
                {"path": str(path)},
            )
        return str(path)

    @staticmethod
    def _require_existing_dir(v: str) -> str:
        """规范化目录路径， 检查是否存在

        Args:
            v (str): 需要规范化的字符串

        Returns:
            str: 规范化的路径字符串
        """
        path = Path(PathCheck._normalize_dir(v))

        if not path.exists():
            raise PydanticCustomError(
                "file_not_found",
                "目录不不存在: {path}",
                {"path": str(path)},
            )

        return str(path)

    @staticmethod
    def _require_existing_file(v: str) -> str:
        """规范化文件路径， 检查是否存在

        Args:
            v (str): 需要规范化的字符串

        Returns:
            str: 规范化的路径字符串
        """
        path = Path(PathCheck._normalize_file(v))

        if not path.exists():
            raise PydanticCustomError(
                "file_not_found",
                "文件不存在: {path}",
                {"path": str(path)},
            )

        return str(path)

    # 暴露元数据
    DirPath = Annotated[str, AfterValidator(_normalize_dir)]
    FilePath = Annotated[str, AfterValidator(_normalize_file)]
    ExistingDir = Annotated[str, AfterValidator(_require_existing_dir)]
    ExistingFile = Annotated[str, AfterValidator(_require_existing_file)]


class Setting(BaseSettings):
    """用于读取环境变量"""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH, extra="forbid", case_sensitive=False
    )

    IS_PRODUCTION: bool = True

    PRINT_CONSOLE_LOG_LEVEL: Literal[
        "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
    ] = "INFO"
    PRINT_CONSOLE_STREAM: str = "ext://sys.stdout"

    PRINT_FILE_LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = (
        "INFO"
    )

    PRINT_FILE_LOG_ENCODING: str = "utf-8"
    PRINT_FILE_LOG_PATH: PathCheck.DirPath = "./logs"
    PRINT_FILE_LOG_WHEN: Literal["S", "M", "H", "D", "W", "midnight"] = "midnight"
    PRINT_FILE_LOG_INTERVAL: Annotated[int, Field(ge=1)] = 1
    PRINT_FILE_LOG_BACKUPCOUNT: Annotated[int, Field(ge=1)] = 30

    DB_CONNECT_STR: Annotated[str, Field(pattern=r"^[a-zA-Z0-9_+\-]+://.+")]

    @field_validator("*", mode="before")
    @classmethod
    def check_delete(cls, v):
        if isinstance(v, str):
            v = v.split("#", 1)[0].strip()  # 删除注释
            if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):  # 剥离引号
                v = v[1:-1]
        return v

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


# 由于静态类型检查无法读取环境变量会报出缺少参数
settings = Setting()  # type: ignore
