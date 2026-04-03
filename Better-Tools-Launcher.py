import json
import os
import shutil
import subprocess
import threading

import requests
import webview
from loguru import logger
from webview import Window

# 配置日志

logger.add("logs/updater.log")


class UpdateManager:
    """现代化更新管理器"""

    def __init__(self):
        self.api_urls = [
            "https://irx999.fun/img/assets/Better-Tools/latest.json",
        ]
        self.temp_dir = "./temp"
        os.makedirs(self.temp_dir, exist_ok=True)
        self.download_path = os.path.join(self.temp_dir, "update.zip")
        self.extract_path = os.path.join(self.temp_dir, "extracted")
        self.main_exe_name = "Better-Tools.exe"  # 主程序名称
        self.password = "123"  # 主程序密码

        # 进度状态
        self.download_progress = 0
        self.extract_progress = 0
        self.current_status = "准备就绪"

    def get_release_info(self):
        """获取最新版本信息"""
        logger.info("获取最新版本信息...")
        for url in self.api_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                logger.error(f"获取版本信息失败: {e}")
                continue
        return None

    def get_local_version(self):
        """获取本地版本"""
        local_file = "./assets/latest.json"
        if os.path.exists(local_file):
            try:
                with open(local_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("version", "0.0.0")
            except Exception as e:
                logger.error(f"读取本地版本失败: {e}")
        return "0.0.0"

    def needs_update(self, release_info):
        """检查是否需要更新"""
        if not release_info or "version" not in release_info:
            return False

        local_version = self.get_local_version()
        remote_version = release_info["version"]

        logger.info(f"本地版本: {local_version}, 远程版本: {remote_version}")
        return local_version != remote_version

    def download_update(self, download_url):
        """下载更新文件并报告进度"""
        try:
            self.current_status = "正在下载..."
            logger.info(f"开始下载: {download_url}")

            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(self.download_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            self.download_progress = int(
                                (downloaded / total_size) * 100
                            )

            self.download_progress = 100
            logger.info("下载完成")
            return True

        except Exception as e:
            logger.error(f"下载失败: {e}")
            return False

    def extract_update(self):
        """解压更新文件并报告进度"""
        try:
            self.current_status = "正在解压..."
            logger.info("开始解压...")

            # 清理之前的解压目录
            if os.path.exists(self.extract_path):
                shutil.rmtree(self.extract_path)

            # 解压文件
            shutil.unpack_archive(self.download_path, self.extract_path)
            self.extract_progress = 100
            logger.info("解压完成")
            return True

        except Exception as e:
            logger.error(f"解压失败: {e}")
            return False

    def terminate_main_process(self):
        """终止主程序进程"""
        try:
            import psutil

            logger.info("检查并终止主程序进程...")

            for proc in psutil.process_iter(["pid", "name"]):
                if proc.info["name"] == self.main_exe_name:
                    logger.info(
                        f"终止进程: {proc.info['name']} (PID: {proc.info['pid']})"
                    )
                    proc.terminate()
                    proc.wait(timeout=5)

        except ImportError:
            logger.warning("psutil未安装，跳过进程终止")
        except Exception as e:
            logger.error(f"终止进程时出错: {e}")

    def replace_files(self):
        """替换文件"""
        try:
            self.current_status = "正在替换文件..."
            logger.info("开始替换文件...")

            if not os.path.exists(self.extract_path):
                logger.error("解压目录不存在")
                return False

            # 复制所有文件到当前目录
            for item_name in os.listdir(self.extract_path):
                source = os.path.join(self.extract_path, item_name)
                target = os.path.join(os.getcwd(), item_name)

                if os.path.isdir(source):
                    if os.path.exists(target):
                        shutil.rmtree(target)
                    shutil.copytree(source, target)
                else:
                    if os.path.exists(target):
                        os.remove(target)
                    shutil.copy2(source, target)

            logger.info("文件替换完成")
            return True

        except Exception as e:
            logger.error(f"文件替换失败: {e}")
            return False

    def cleanup(self):
        """清理临时文件"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info("临时文件清理完成")
        except Exception as e:
            logger.error(f"清理失败: {e}")

    def start_main_app(self):
        """启动主程序"""
        try:
            main_exe = self.main_exe_name
            if os.path.exists(main_exe):
                logger.info("启动主程序...")
                # 使用 -s 参数和密码启动
                subprocess.Popen([main_exe, "-s", self.password])
                return True, "主程序启动成功"
            else:
                error_msg = "主程序不存在/或者当前是开发者模式"
                logger.error(error_msg)
                return False, error_msg
        except Exception as e:
            error_msg = f"启动主程序失败: {e}"
            logger.error(error_msg)
            return False, error_msg


class UpdaterAPI:
    """Web API接口"""

    def __init__(self):
        self.update_manager = UpdateManager()
        self.update_thread = None

    def get_status(self):
        """获取当前状态"""
        return {
            "download_progress": self.update_manager.download_progress,
            "extract_progress": self.update_manager.extract_progress,
            "current_status": self.update_manager.current_status,
        }

    def check_and_update(self):
        """检查更新并执行更新流程"""

        def update_process():
            try:
                # 获取版本信息
                release_info = self.update_manager.get_release_info()
                if not release_info:
                    self.update_manager.current_status = "无法获取版本信息"
                    return

                # 检查是否需要更新
                if not self.update_manager.needs_update(release_info):
                    self.update_manager.current_status = "已是最新版本"
                    # 直接启动主程序
                    self.update_manager.start_main_app()
                    return

                # 获取下载URL
                if "browser_download_url" in release_info:
                    download_url = release_info["browser_download_url"]
                elif "assets" in release_info and len(release_info["assets"]) > 0:
                    download_url = release_info["assets"][0].get(
                        "browser_download_url", ""
                    )
                else:
                    self.update_manager.current_status = "下载链接无效"
                    return

                if not download_url:
                    self.update_manager.current_status = "下载链接为空"
                    return

                # 下载更新
                if not self.update_manager.download_update(download_url):
                    self.update_manager.current_status = "下载失败"
                    return

                # 解压更新
                if not self.update_manager.extract_update():
                    self.update_manager.current_status = "解压失败"
                    return

                # 终止主程序
                self.update_manager.terminate_main_process()

                # 替换文件
                if not self.update_manager.replace_files():
                    self.update_manager.current_status = "文件替换失败"
                    return

                # 清理
                self.update_manager.cleanup()

                # 完成
                self.update_manager.current_status = "更新完成！点击启动按钮运行程序"

            except Exception as e:
                logger.error(f"更新过程出错: {e}")
                self.update_manager.current_status = f"更新失败: {str(e)}"

        self.update_thread = threading.Thread(target=update_process, daemon=True)
        self.update_thread.start()
        return {"success": True}

    def launch_app(self):
        """启动应用程序"""
        success, message = self.update_manager.start_main_app()
        if success:
            logger.info("主程序启动成功")
            self.update_manager.current_status = "启动成功"
            return {"success": True, "message": message}
        else:
            logger.error("主程序启动失败")
            self.update_manager.current_status = "启动失败"
            return {"success": False, "message": message}

    def windows_destroy(self):
        """测试"""
        logger.info("windows_destroy")
        window: Window = webview.windows[0]
        window.destroy()


def main():
    """主函数"""
    api = UpdaterAPI()

    # 获取屏幕信息以实现窗口居中
    try:
        # 获取主屏幕（通常是第一个屏幕）
        primary_screen = webview.screens[0]
        screen_width = primary_screen.width
        screen_height = primary_screen.height

        # 计算居中位置

    except (IndexError, AttributeError):
        # 如果无法获取屏幕信息，使用默认位置
        screen_width = 2560
        screen_height = 1440

    # 创建窗口
    window = webview.create_window(
        "Better-Tools-Launcher",
        url="Better-Tools-Launcher.html",
        js_api=api,
        width=600,
        height=300,
        resizable=False,
        frameless=False,
        transparent=True,
        shadow=True,
        easy_drag=True,
        x=(screen_width - 600) // 2,
        y=(screen_height - 300) // 2,
    )
    setattr(window, "name", "Better-Tools-Launcher")
    # 启动应用 - 正确的调用方式
    webview.start(debug=True)


if __name__ == "__main__":
    main()
