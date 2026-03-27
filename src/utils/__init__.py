import os
import sys

from .config_manager import ConfigManager
from .config_reader import Config_reader


def get_resource_path(relative_path: list[str] | str):
    """
    获取资源的绝对路径。
    适用于开发环境和 PyInstaller 打包后的环境。

    :param relative_path: 相对于项目根目录或 spec 文件中 defined path 的路径
    :return: 绝对路径字符串
    """
    if hasattr(sys, "_MEIPASS"):
        base_path = getattr(sys, "_MEIPASS", os.getcwd())

    else:
        # base_path = os.path.abspath(".")
        base_path = os.getcwd()

    if isinstance(relative_path, str):
        # 绝对路径
        if os.path.exists(os.path.join(base_path, relative_path)):
            return os.path.join(base_path, relative_path)
        # 相对路径
        if os.path.exists(relative_path):
            return relative_path
    # 使用绝对路径
    for i in relative_path:
        if os.path.exists(os.path.join(base_path, i)):
            return os.path.join(base_path, i)

    # 使用相对路径
    for i in relative_path:
        if os.path.exists(i):
            return i
    raise FileNotFoundError(f"{relative_path} not found")


__all__ = [
    "Config_reader",
    "ConfigManager",
    "get_resource_path",
]
