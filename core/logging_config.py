import logging
import logging.config
import sys
import tarfile
from datetime import UTC, datetime, timedelta
from logging import getLogger
from pathlib import Path

from yaml import safe_load

from core.config import settings

logger = getLogger(__name__)

OPEN_ENCODING = settings.PRINT_FILE_LOG_ENCODING
LOGGING_CONFIG_PATH = Path(__file__).resolve().parent / "logging.yaml"
LOGS_PATH = Path(settings.PRINT_FILE_LOG_PATH)
DELETE_LOG_TIME = datetime.now(tz=UTC).astimezone() - timedelta(
    days=settings.PRINT_FILE_LOG_BACKUPCOUNT
)


def logging_init() -> None:
    """用于初始化日志系统
    初始化日志系统,并打包删除旧日志
    """
    compress_old_logs(log_path=LOGS_PATH, keep_file_naem_list=[])

    # 删除旧的日志压缩包
    delete_old_logs(log_path=LOGS_PATH, delete_log_time=DELETE_LOG_TIME)

    try:
        with open(str(LOGGING_CONFIG_PATH), "r", encoding=OPEN_ENCODING) as f:
            config = safe_load(f)

            # 覆盖参数
            config["handlers"]["console"]["level"] = settings.get_console_loglevel
            config["handlers"]["console"]["stream"] = settings.PRINT_CONSOLE_STREAM

            config["handlers"]["file"]["level"] = settings.get_file_loglevel
            config["handlers"]["file"]["encoding"] = settings.PRINT_FILE_LOG_ENCODING
            config["handlers"]["file"]["filename"] = (
                Path(settings.PRINT_FILE_LOG_PATH).resolve() / "log.log"
            )
            config["handlers"]["file"]["interval"] = settings.PRINT_FILE_LOG_INTERVAL

            logging.config.dictConfig(config)

    except UnicodeDecodeError as e:
        print("日志配置错误-编码错误 (尝试的编码%s)", OPEN_ENCODING, e, file=sys.stderr)
    except ValueError as e:
        print("日志配置错误-配置值错误", e, file=sys.stderr)
        raise SystemExit(1) from e
    except TypeError as e:
        print("日志配置错误-配置类型错误", e, file=sys.stderr)
        raise SystemExit(1) from e
    except KeyError as e:
        print("日志配置错误-缺少配置键", e, file=sys.stderr)
        raise SystemExit(1) from e
    except AttributeError as e:
        print("日志配置错误-配置属性错误", e, file=sys.stderr)
        raise SystemExit(1) from e
    except ImportError as e:
        print("日志配置错误-导入失败", e, file=sys.stderr)
        raise SystemExit(1) from e
    except OSError as e:
        print("日志配置错误-系统错误", e, file=sys.stderr)
        raise SystemExit(1) from e
    except Exception as e:
        print("日志配置错误-未知错误", e, file=sys.stderr)
        raise SystemExit(1) from e

    logger.info("日志初始化完成")


def compress_old_logs(log_path: Path, keep_file_naem_list: list[str]) -> None:
    """将旧的Log文件压缩
    找到log_path下"*.log*"成立且不在keep_file_path_list里的文件并将他们打包
    删除keep_file_naem_list其余的log文件
    Args:
        compress_name (str): 压缩后的名称
        log_path (Path): Log文件目录
        keep_file_naem_list (list[str]): 需要保留文件的Path列表
    """
    if any(LOGS_PATH.iterdir()):  # 为非空
        # 压缩旧日志
        # 寻找最早的文件修改日期作为压缩包的名称
        first_file_modified_date = float("inf")
        for file in LOGS_PATH.glob("*.log*"):
            first_file_modified_date = min(
                file.stat().st_mtime, first_file_modified_date
            )

        first_file_modified_date = datetime.fromtimestamp(
            first_file_modified_date, tz=UTC
        ).astimezone()  # 转换格式
        compress_name = (
            f"log_{first_file_modified_date.strftime('%Y-%m-%d_%H_%M')}.tar.gz"
        )

    log_path = log_path.resolve()  # 转换为绝对路径
    compress_log_path = log_path / compress_name

    keep_file_abs_path_list = [
        log_path / Path(file_abs_path) for file_abs_path in keep_file_naem_list
    ]  # 转换为绝对路径

    need_compress_log_path = [  # 需要压缩文件的绝对路径
        file_resolve_path
        for file in log_path.glob("*.log*")
        if (file_resolve_path := file.resolve())  # 转换为绝对路径
        not in keep_file_abs_path_list  # 排除不需要压缩的文件
    ]

    with tarfile.open(compress_log_path, "w:gz") as tar:
        for file_path in need_compress_log_path:
            file_mtime = (
                datetime.fromtimestamp(file_path.stat().st_mtime, tz=UTC)
                .astimezone()
                .strftime("%Y-%m-%d_%H_%M")  # 格式化名称
            )  # 获取文件修改时间作为文件名

            file_name = f"log_{file_mtime}.log"
            tar.add(
                str(file_path), arcname=file_name
            )  # 统一名称, 防止不同when配置造成的名称不同

    # 删除keep_file_path_list其余的log文件
    for file_path in need_compress_log_path:
        file_path.unlink()


def delete_old_logs(log_path: Path, delete_log_time: datetime) -> None:
    """删除旧的压缩包(Log)文件
    删除所有大于等于delete_log_time的压缩包

    Args:
        log_path (Path): 压缩包文件目录
        delete_log_time (datetime): 删除阈值
    """
    delete_log_time_stamp = delete_log_time.timestamp()  # 转换为时间戳

    for file in log_path.glob("*.tar.gz*"):
        file_resolve_path = file.resolve()
        if file_resolve_path.stat().st_ctime <= delete_log_time_stamp:  # 超出阈值
            file_resolve_path.unlink()
