"""配置信息只读模块

支持读取 TOML 和 JSON 格式的配置文件，提供配置项的获取和管理功能。
"""

import datetime
import os
from typing import Any, Dict

from ._config_io import load_config_file


class Config_reader:
    """只读配置读取器，支持 TOML/JSON 与多候选路径回退。"""

    def __init__(self, filename: str | list[str]) -> None:
        """
        Args:
            filename: 配置文件路径，单个路径或路径列表（按顺序找第一个存在的）。
                列表中的 None 条目会被跳过。
        """
        if isinstance(filename, list):
            found_file = next(
                (f for f in filename if f is not None and os.path.exists(f)), None
            )
            if found_file is None:
                raise FileNotFoundError(
                    f"在列表 {filename} 中没有找到任何存在的配置文件"
                )
            filename = found_file

        self.filename = filename
        self.config: dict = {}
        self.mtime = datetime.datetime.fromtimestamp(
            os.path.getmtime(filename)
        ).strftime("%Y-%m-%d %H:%M:%S")

        self.reload()

    def get(self, key: str, default: Any = None) -> Any:
        self.reload()
        return self.config.get(key, default)

    def items(self):
        return self.config.items()

    def __getitem__(self, key: str) -> Dict[str, Any] | Any:
        self.reload()
        if key not in self.config:
            raise KeyError(f"配置文件中没有找到 {key} 的配置")
        return self.config[key]

    def __len__(self) -> int:
        self.reload()
        return len(self.config)

    def reload(self) -> None:
        try:
            self.config = load_config_file(self.filename)
        except FileNotFoundError:
            print(f"[ConfigReader] 警告：配置文件 {self.filename} 不存在！")
        except Exception as e:
            print(f"[ConfigReader] 错误：加载配置文件 {self.filename} 时发生异常：{e}")
