"""logging上下文,用于request_id注入"""

import logging
from contextvars import ContextVar

request_id: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    """request_id前缀记录"""

    def filter(self, record: logging.LogRecord) -> bool:
        """request_id前缀

        Args:
            record: 日志记录

        Returns:
            bool: True(保留)
        """

        record.request_id = request_id.get()
        return True


class RequestIdFormatter(logging.Formatter):
    """logging Formatter
    在有request_id时记录否则为空
    """

    def format(self, record: logging.LogRecord) -> str:
        """logging Formatter

        Args:
            record: 日志记录

        Returns:
            str: 格式化字符串
        """

        request_id = getattr(record, "request_id", None)
        record.request_id = (
            f" - [{request_id}] " if request_id == None or not request_id else ""
        )

        return super().format(record)
