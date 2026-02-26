import importlib.util
import os
from dataclasses import dataclass

from loguru import logger

from src.utils import Config_reader

logger.add("logs/ModulesMnager.log", format="{time} {level} {message}")

PYPROJECT = Config_reader(["pyproject.toml", "assets/pyproject.toml"])


@dataclass
class Module_info:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.mtime = None
        self.version = None
        self.description = None
        self.changelog = None


class ModulesMnager:
    """项目模块管理"""

    def __init__(self, path, view):
        self.path = path
        self.view = view
        self.project_toml = PYPROJECT


# plugin_manager.py


def load_plugins(plugin_dir):
    plugins = {}
    for item in os.listdir(plugin_dir):
        plugin_path = os.path.join(plugin_dir, item)
        if os.path.isdir(plugin_path) and os.path.exists(
            os.path.join(plugin_path, "src")
        ):
            spec = importlib.util.spec_from_file_location(
                f"plugins.{item}.main", os.path.join(plugin_path, "src", "__init__.py")
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            plugins[item] = module
    return plugins
