"""
配置信息读取模块

支持读取TOML和JSON格式的配置文件，提供配置项的获取和管理功能。
"""

import datetime
import json
import os
import tomllib
from typing import Any, Dict


class Config_reader:
    """配置信息读取类

    支持读取TOML和JSON格式的配置文件，提供配置项的获取和管理功能。
    """

    def __init__(self, filename: str | list[str]) -> None:
        """
        初始化配置读取器

        Args:
            filename (str): 配置文件路径
        """

        # 修改: 支持文件列表，按顺序查找第一个存在的文件
        if isinstance(filename, list):
            found_file = None
            for f in filename:
                if os.path.exists(f):
                    found_file = f
                    break
            if found_file is None:
                raise FileNotFoundError(
                    f"在列表 {filename} 中没有找到任何存在的配置文件"
                )
            filename = found_file

        self.filename = filename
        self.config = {}
        self.mtime = datetime.datetime.fromtimestamp(
            os.path.getmtime(filename)
        ).strftime("%Y-%m-%d %H:%M:%S")

        self.reload()

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项的值

        Args:
            key (str): 配置项键名
            default (Any, optional): 默认值

        Returns:
            Any: 配置项的值或默认值
        """
        self.reload()
        return self.config.get(key, default)

    def items(self):
        """
        获取所有配置项

        Returns:
            dict_items: 所有配置项的键值对
        """
        return self.config.items()

    def __getitem__(self, key: str) -> Dict[str, Any] | Any:
        """
        通过索引获取配置项

        Args:
            key (str): 配置项键名

        Returns:
            Dict[str, Any]: 配置项的值

        Raises:
            KeyError: 当配置项不存在时抛出异常
        """
        try:
            self.reload()
            if key not in self.config:
                raise KeyError(f"配置文件中没有找到 {key} 的配置")
            return self.config[key]
        except KeyError as e:
            raise e

    def __len__(self) -> int:
        """
        获取配置项数量

        Returns:
            int: 配置项数量
        """
        self.reload()
        return len(self.config)

    def reload(self) -> None:
        """重新加载配置文件"""
        try:
            with open(self.filename, "rb") as f:
                match self.filename.split(".")[-1]:
                    case "toml":
                        self.config = tomllib.load(f)
                    case "json":
                        self.config = json.load(f)
                    case _:
                        raise ValueError("不支持的配置文件格式")

        except FileNotFoundError:
            print(f"配置文件 {self.filename}不存在！")
