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
    try:
        # PyInstaller 打包后，会将文件解压到临时文件夹，路径保存在 _MEIPASS 中
        base_path = sys._MEIPASS  # type: ignore
    except AttributeError:
        # 正常开发环境下，使用当前脚本所在的目录
        base_path = os.path.abspath(".")
        base_path = os.getcwd()
        # 或者更严谨一点，使用 __file__ (但在某些交互式环境可能失效)
        # base_path = os.path.dirname(os.path.abspath(__file__))
    if isinstance(relative_path, str):
        if os.path.exists(os.path.join(base_path, relative_path)):
            return os.path.join(base_path, relative_path)

    for i in relative_path:
        if os.path.exists(os.path.join(base_path, i)):
            return os.path.join(base_path, i)
    for i in relative_path:
        if os.path.exists(i):
            return i
    raise FileNotFoundError(f"{relative_path} not found")


__all__ = [
    "Config_reader",
    "ConfigManager",
    "get_resource_path",
]
