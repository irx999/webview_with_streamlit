"""
配置信息读取与写入模块

支持读取和写入TOML和JSON格式的配置文件，提供配置项的获取和管理功能。
"""

import datetime
import json
import os
import tomllib
from typing import Any, Dict

import tomli_w
from loguru import logger

logger.add("logs/config.log", rotation="1 MB")


class ConfigManager:
    """配置信息读取与写入类

    支持读取和写入TOML和JSON格式的配置文件，提供配置项的获取和管理功能。
    """

    def __init__(self, filename: str, config_name: str) -> None:
        """
        初始化配置管理器

        Args:
            filename (str): 配置文件路径
        """
        self.filename = filename
        self.config_name = config_name

        self.all_config: dict = {}
        self.reload()

        self.config: dict = self.all_config.get(config_name, {})
        self.mtime = (
            datetime.datetime.fromtimestamp(os.path.getmtime(filename)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            if os.path.exists(filename)
            else None
        )

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

    def set(self, key: str, value: Any) -> None:
        """
        设置配置项的值并保存到文件

        Args:
            key (str): 配置项键名
            value (Any): 配置项的值
        """
        old_value = self.config.get(key)
        self.config[key] = value
        logger.info(f"{self.config_name} -- {key} : {old_value} --> {value}")
        self.save()

    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        更新多个配置项并保存到文件

        Args:
            config_dict (Dict[str, Any]): 包含多个配置项的字典
        """
        # 记录即将更新的配置项及其变化
        for key, value in config_dict.items():
            old_value = self.config.get(key)
            if key in self.config:
                if old_value != value:
                    logger.info(
                        f"{self.config_name} -- {key} : {old_value} --> {value}"
                    )
            else:
                logger.info(f"新增配置项 {key} : {value}")

        self.config.update(config_dict)
        self.save()

    def items(self):
        """
        获取所有配置项

        Returns:
            dict_items: 所有配置项的键值对
        """
        return self.config.items()

    def keys(self):
        """
        获取所有配置项的键

        Returns:
            dict_keys: 所有配置项的键
        """
        return self.config.keys()

    def values(self):
        """
        获取所有配置项的值

        Returns:
            dict_values: 所有配置项的值
        """
        return self.config.values()

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

    def __setitem__(self, key: str, value: Any) -> None:
        """
        通过索引设置配置项

        Args:
            key (str): 配置项键名
            value (Any): 配置项的值
        """
        self.config[key] = value
        logger.info(f"已设置 {key} 的值为 {value}")
        self.save()

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
            if os.path.exists(self.filename):
                with open(self.filename, "rb") as f:
                    match self.filename.split(".")[-1]:
                        case "toml":
                            self.all_config = tomllib.load(f)
                        case "json":
                            self.all_config = json.load(f)
                        case _:
                            raise ValueError("不支持的配置文件格式")
            else:
                # 如果文件不存在，初始化为空字典
                self.all_config = {self.config_name: {}}
        except FileNotFoundError:
            print(f"配置文件 {self.filename} 不存在！将创建新文件。")
            self.all_config = {self.config_name: {}}
        except Exception as e:
            print(f"加载配置文件时发生错误: {e}")
            self.all_config = {self.config_name: {}}

    def save(self) -> None:
        """保存配置到文件"""
        self.all_config.update({self.config_name: self.config})
        try:
            # 确保目录存在
            directory = os.path.dirname(self.filename)
            if directory:
                os.makedirs(directory, exist_ok=True)

            file_ext = self.filename.split(".")[-1]

            # 默认行为：全量覆盖写入 (适用于 JSON 或 更新失败的 TOML)
            # 根据文件类型决定打开模式：toml 需要二进制模式 'wb'，json 需要文本模式 'w'
            mode = "wb" if file_ext == "toml" else "w"

            if mode == "wb":
                with open(self.filename, mode) as f:
                    match file_ext:
                        case "toml":
                            tomli_w.dump(self.all_config, f)  # type: ignore
                        case _:
                            raise ValueError(f"不支持的配置文件格式：.{file_ext}")
            else:
                with open(self.filename, mode, encoding="utf-8") as f:
                    match file_ext:
                        case "json":
                            json.dump(self.all_config, f, indent=4, ensure_ascii=False)
                        case _:
                            raise ValueError(f"不支持的配置文件格式：.{file_ext}")

            # 更新修改时间
            self.mtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"保存配置文件时发生错误：{e}")

    def delete(self, key: str) -> bool:
        """
        删除指定的配置项

        Args:
            key (str): 要删除的配置项键名

        Returns:
            bool: 是否删除成功
        """
        if key in self.config:
            del self.config[key]
            self.save()
            return True
        return False

    def clear(self) -> None:
        """清空所有配置项并保存"""
        self.config.clear()
        self.save()

    def set_nested(self, key: str, sub_key: str, value: Any) -> None:
        """
        设置嵌套字典中特定键的子键值，并重新读取文件以避免其他实例修改的影响

        Args:
            key (str): 主键名
            sub_key (str): 子键名
            value (Any): 子键对应的值
        """
        # 重新加载配置，确保获取最新的配置内容
        self.reload()
        if key not in self.config:
            self.config[key] = {}
        if not isinstance(self.config[key], dict):
            raise TypeError(f"键 '{key}' 不是字典类型，无法设置子键 '{sub_key}'")
        self.config[key][sub_key] = value
        self.save()

    def get_nested(self, key: str, sub_key: str, default: Any = None) -> Any:
        """
        获取嵌套字典中特定键的子键值

        Args:
            key (str): 主键名
            sub_key (str): 子键名
            default (Any, optional): 默认值

        Returns:
            Any: 子键的值或默认值
        """
        self.reload()
        if (
            key in self.config
            and isinstance(self.config[key], dict)
            and sub_key in self.config[key]
        ):
            return self.config[key][sub_key]
        return default

    def update_nested(self, key: str, sub_dict: Dict[str, Any]) -> None:
        """
        更新嵌套字典中特定键的多个子键值

        Args:
            key (str): 主键名
            sub_dict (Dict[str, Any]): 包含多个子键值的字典
        """
        self.reload()
        if key not in self.config:
            self.config[key] = {}
        if not isinstance(self.config[key], dict):
            raise TypeError(f"键 '{key}' 不是字典类型，无法更新子键")
        self.config[key].update(sub_dict)
        self.save()
