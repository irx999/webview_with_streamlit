"""TOML / JSON 配置文件读写助手 —— Config_reader 与 ConfigManager 共享。"""

import json
import os
import tomllib
from typing import Any

import tomli_w


def load_config_file(filename: str) -> dict[str, Any]:
    """按扩展名读取 TOML 或 JSON 配置文件并返回 dict。"""
    ext = filename.split(".")[-1]
    with open(filename, "rb") as f:
        match ext:
            case "toml":
                return tomllib.load(f)
            case "json":
                return json.load(f)
            case _:
                raise ValueError(f"不支持的配置文件格式：.{ext}")


def dump_config_file(filename: str, data: dict[str, Any]) -> None:
    """按扩展名写入 TOML 或 JSON 配置文件。"""
    directory = os.path.dirname(filename)
    if directory:
        os.makedirs(directory, exist_ok=True)
    ext = filename.split(".")[-1]
    match ext:
        case "toml":
            with open(filename, "wb") as f:
                tomli_w.dump(data, f)  # type: ignore[arg-type]
        case "json":
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        case _:
            raise ValueError(f"不支持的配置文件格式：.{ext}")
