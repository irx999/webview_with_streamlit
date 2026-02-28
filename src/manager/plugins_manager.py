import os
import re
import sys
from dataclasses import dataclass

import requests
from loguru import logger

from src.utils import Config_reader

logger.add("logs/ModulesMnager.log", format="{time} {level} {message}")


@dataclass
class Module_info:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.mtime = None
        self.version = None
        self.description = None
        self.changelog = None


class Plugins_Manager:
    """项目模块管理"""

    def __init__(self):
        pass

    def load_plugins(self, plugin_dir="plugins"):
        plugins_dict = {
            "ps_of_py": {
                "pyproject_toml": Config_reader(
                    [f"{plugin_dir}/ps_of_py/pyproject.toml"]
                )
            }
        }
        return plugins_dict

    def is_development_mode(self):
        """判断是否是开发模式"""
        # 如果是打包后的可执行文件，则不是开发模式
        if getattr(sys, "frozen", False):
            return False

        # 如果项目根目录存在 .git 文件夹，则认为是开发模式
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        if os.path.exists(os.path.join(project_root, ".git")):
            return True

        # 默认为开发模式
        return True

    def check_for_updates(self, plugins_name, github_repo, branch="main") -> bool:
        """
        检查更新 - 从GitHub仓库的pyproject.toml文件获取版本信息
        :param github_repo: GitHub仓库名，例如 'username/repo'
        :param branch: 分支名，默认为main
        :return: 是否有更新
        """
        if self.is_development_mode():
            logger.info("当前为开发模式，跳过更新检查")
            # return False

        try:
            # 构造请求URL以获取pyproject.toml文件
            pyproject_url = f"https://raw.githubusercontent.com/{github_repo}/{branch}/pyproject.toml"

            response = requests.get(pyproject_url)
            if response.status_code != 200:
                logger.error(
                    f"无法获取远程pyproject.toml文件，状态码: {response.status_code}"
                )
                return False

            # 解析远程pyproject.toml文件以获取版本
            remote_pyproject_content = response.text

            # 查找版本信息（支持不同的toml格式）
            version_match = re.search(
                r'version\s*=\s*["\']([^"\']+)["\']', remote_pyproject_content
            )

            if not version_match:
                logger.error("无法从远程pyproject.toml文件中提取版本信息")
                return False

            remote_version = version_match.group(1)
            plugins_porject_toml = Config_reader(
                [f"plugins/{plugins_name}/pyproject.toml"]
            )
            current_version = plugins_porject_toml["project"]["version"]

            logger.info(f"本地版本: {current_version}, 远程版本: {remote_version}")

            # 比较版本号
            if self.compare_versions(current_version, remote_version):
                logger.info("发现新版本，建议更新")
                return True
            else:
                logger.info("当前已是最新版本")
                return False

        except Exception as e:
            logger.error(f"检查更新时发生错误: {e}")
            return False

    def compare_versions(self, current, remote):
        """
        比较版本号
        :param current: 当前版本
        :param remote: 远程版本
        :return: 如果远程版本更新则返回True，否则返回 False
        """
        try:
            # 将版本号拆分为数字列表进行比较
            current_parts = [int(x) for x in current.replace("v", "").split(".")]
            remote_parts = [int(x) for x in remote.replace("v", "").split(".")]

            # 补齐长度
            max_len = max(len(current_parts), len(remote_parts))
            current_parts.extend([0] * (max_len - len(current_parts)))
            remote_parts.extend([0] * (max_len - len(remote_parts)))

            # 按位比较版本号
            for curr, rem in zip(current_parts, remote_parts):
                if rem > curr:
                    return True
                elif rem < curr:
                    return False

            return False  # 版本相同

        except Exception as e:
            logger.error(f"版本比较失败: {e}")
            # 如果版本比较失败，尝试字符串比较
            return remote > current  # 字符串比较作为备选方案
