import os
import re
import sys
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

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

    def update_plugin(self, plugins_name, github_repo, branch="main") -> bool:
        """
        更新插件 - 从GitHub仓库下载并安装最新版本的插件
        :param plugins_name: 插件名称
        :param github_repo: GitHub仓库名，例如 'username/repo'
        :param branch: 分支名，默认为main
        :return: 更新是否成功
        """
        if self.is_development_mode():
            logger.info("当前为开发模式，跳过插件更新")
            return False

        try:
            # 创建临时目录用于下载和解压
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # 步骤1: 下载最新的源代码
                logger.info(f"开始下载插件 {plugins_name} 的最新版本...")
                download_url = f"https://github.com/{github_repo}/archive/refs/heads/{branch}.zip"
                zip_path = temp_path / f"{plugins_name}.zip"
                
                response = requests.get(download_url)
                if response.status_code != 200:
                    logger.error(f"下载插件失败，状态码: {response.status_code}")
                    return False
                
                with open(zip_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"插件下载完成: {zip_path}")
                
                # 步骤2: 解压下载的文件
                extract_path = temp_path / "extracted"
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                logger.info(f"插件解压完成: {extract_path}")
                
                # 步骤3: 找到解压后的插件目录
                # GitHub下载的zip文件会包含一个顶层目录，格式为 repo-name-branch
                extracted_dirs = list(extract_path.iterdir())
                if not extracted_dirs:
                    logger.error("解压后的目录为空")
                    return False
                
                repo_dir = extracted_dirs[0]  # 获取第一个（也是唯一一个）目录
                if not repo_dir.is_dir():
                    logger.error("解压后的路径不是目录")
                    return False
                
                logger.info(f"找到插件源码目录: {repo_dir}")
                
                # 步骤4: 备份当前插件（如果存在）
                plugin_path = Path(f"plugins/{plugins_name}")
                backup_path = None
                if plugin_path.exists():
                    backup_path = Path(f"plugins/{plugins_name}_backup")
                    if backup_path.exists():
                        shutil.rmtree(backup_path)
                    shutil.copytree(plugin_path, backup_path)
                    logger.info(f"已备份当前插件到: {backup_path}")
                
                # 步骤5: 删除旧插件目录（如果存在）
                if plugin_path.exists():
                    shutil.rmtree(plugin_path)
                    logger.info(f"已删除旧插件目录: {plugin_path}")
                
                # 步骤6: 复制新插件文件
                shutil.copytree(repo_dir, plugin_path)
                logger.info(f"新插件已安装到: {plugin_path}")
                
                # 步骤7: 验证更新是否成功
                new_config = Config_reader([str(plugin_path / "pyproject.toml")])
                new_version = new_config["project"]["version"]
                logger.info(f"插件更新成功！新版本: {new_version}")
                
                return True
                
        except Exception as e:
            logger.error(f"插件更新过程中发生错误: {e}")
            # 如果有备份，尝试恢复
            plugin_path = Path(f"plugins/{plugins_name}")
            backup_path = Path(f"plugins/{plugins_name}_backup")
            if backup_path.exists():
                try:
                    if plugin_path.exists():
                        shutil.rmtree(plugin_path)
                    shutil.copytree(backup_path, plugin_path)
                    logger.info("已从备份恢复插件")
                    shutil.rmtree(backup_path)
                except Exception as restore_error:
                    logger.error(f"恢复备份时发生错误: {restore_error}")
            
            return False