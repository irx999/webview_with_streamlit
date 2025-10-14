import json
import os
import shutil

import requests
import webview
from loguru import logger

logger.add("logs/updater.log", format="{time} {level} {message}")


# 添加一个简单的前端页面函数
def create_simple_frontend():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Updater</title>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
            }
            button {
                background-color: #4CAF50;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
                width: 100%;
                margin: 10px 0;
            }
            button:hover {
                background-color: #45a049;
            }
            button:disabled {
                background-color: #cccccc;
                cursor: not-allowed;
            }
            #log {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 4px;
                height: 300px;
                overflow-y: scroll;
                padding: 10px;
                font-family: monospace;
                white-space: pre-wrap;
            }
            .status {
                text-align: center;
                font-weight: bold;
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>应用程序更新器</h1>
            <div class="status" id="status">准备就绪</div>
            <button id="checkBtn" onclick="checkUpdate()">检查更新</button>
            <button id="updateBtn" onclick="startUpdate()" disabled>开始更新</button>
            <div id="log"></div>
        </div>

        <script>
            let updateAvailable = false;
            let downloadUrl = '';
            let fileName = '';

            function logMessage(message) {
                const logElement = document.getElementById('log');
                const timestamp = new Date().toLocaleTimeString();
                logElement.innerHTML += `[${timestamp}] ${message}\\n`;
                logElement.scrollTop = logElement.scrollHeight;
            }

            function updateStatus(status) {
                document.getElementById('status').innerText = status;
            }

            async function checkUpdate() {
                const checkBtn = document.getElementById('checkBtn');
                const updateBtn = document.getElementById('updateBtn');
                
                checkBtn.disabled = true;
                updateStatus('正在检查更新...');
                logMessage('开始检查更新...');
                
                try {
                    const response = await fetch('/check_update', {method: 'POST'});
                    const result = await response.json();
                    
                    if (result.available) {
                        updateAvailable = true;
                        downloadUrl = result.download_url;
                        fileName = result.file_name;
                        
                        updateBtn.disabled = false;
                        updateStatus(`发现新版本: ${result.version}`);
                        logMessage(`发现新版本: ${result.version}`);
                        logMessage(`下载地址: ${downloadUrl}`);
                    } else {
                        updateStatus('当前已是最新版本');
                        logMessage('当前已是最新版本');
                    }
                } catch (error) {
                    updateStatus('检查更新失败');
                    logMessage(`检查更新失败: ${error}`);
                } finally {
                    checkBtn.disabled = false;
                }
            }

            async function startUpdate() {
                const checkBtn = document.getElementById('checkBtn');
                const updateBtn = document.getElementById('updateBtn');
                
                checkBtn.disabled = true;
                updateBtn.disabled = true;
                
                updateStatus('正在更新...');
                logMessage('开始更新...');
                
                try {
                    const response = await fetch('/start_update', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            download_url: downloadUrl,
                            file_name: fileName
                        })
                    });
                    
                    if (response.ok) {
                        updateStatus('更新完成');
                        logMessage('更新完成，请重启应用程序');
                    } else {
                        throw new Error('更新失败');
                    }
                } catch (error) {
                    updateStatus('更新失败');
                    logMessage(`更新失败: ${error}`);
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content


logger.add("logs/updater.log", format="{time} {level} {message}")


class Updater:
    """应用程序更新器，负责检查、下载、解压和安装最新版本的应用程序。"""

    def __init__(self):
        # 进程名称列表
        self.process_names = [
            "March7th Assistant.exe",
            "March7th Launcher.exe",
            "flet.exe",
            "gui.exe",
        ]
        # API地址列表
        self.api_urls = [
            "https://d.irx999.fun:2333/index.php?action=download&file=%E6%B5%8B%E8%AF%95%2Flatest.json",
        ]
        # 临时目录路径
        self.temp_path = os.path.abspath("./temp")
        os.makedirs(self.temp_path, exist_ok=True)

        # 初始化文件名
        self.file_name = ""

        # 初始化文件路径（将在_get_paths中更新）
        self.download_file_path = os.path.join(self.temp_path, "cache.zip")
        self.extract_folder_path = os.path.join(self.temp_path, "extract")
        self.cover_folder_path = os.getcwd()

        # 需要删除的文件路径列表
        self.delete_file_path_list = [
            "assets",
            "app-0.0.1",
            "My_app.exe",
        ]

        # 发布信息
        self.release_info = {}

    def get_release_info(self):
        logger.info("🌟 获取最新版本信息...")
        for url in self.api_urls:
            lastst_info = requests.get(url)
            if lastst_info.status_code == 200:
                self.release_info = lastst_info.json()
                return
        logger.error(f"❌ 获取最新版本信息失败: {lastst_info.status_code}")

    def get_local_version(self):
        logger.info("🌟 获取本地版本信息...")
        if os.path.exists("./assets/latest.json"):
            with open("./assets/latest.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                return data.get("version", "0.0.0")
        logger.error("❌ 本地信息不存在 将返回0.0.0")
        return "0.0.0"

    def compare_versions(self):
        """处理发布数据，获取下载URL并比较版本。"""
        # 确保有版本信息
        if "version" not in self.release_info:
            logger.warning("❌ 最新版本信息中没有版本号")
            return False

        release_version = self.release_info["version"]
        local_version = self.get_local_version()

        logger.info(f"最新版本: {release_version}")
        logger.info(f"本地版本: {local_version}")
        if release_version != local_version:
            return True
        return False

    def download_file(self):
        try:
            logger.info("🌟 开始下载...")
            os.makedirs(self.temp_path, exist_ok=True)

            url = self.release_info["download_url"]

            with requests.get(url) as response:
                response.raise_for_status()
                with open(self.download_file_path, "wb") as file:
                    file.write(response.content)
            logger.info(f"下载完成: {self.download_file_path}")
        except Exception as e:
            logger.error(f"下载失败: {e}")
            if os.path.exists(self.download_file_path):
                os.remove(self.download_file_path)

    def extract_file(self):
        """解压下载的文件。"""
        try:
            logger.info("🌟 开始解压...")
            shutil.unpack_archive(self.download_file_path, self.extract_folder_path)
            logger.info(f"解压完成: {self.extract_folder_path}")
            return True
        except Exception as e:
            logger.error(f"解压失败: {e}")
            return False

    def terminate_processes(self):
        # 确保psutil模块已导入
        try:
            import psutil  # type: ignore #

            logger.info("开始终止进程...")
            for proc in psutil.process_iter(attrs=["pid", "name"]):
                if proc.info["name"] in self.process_names:
                    try:
                        proc.terminate()
                        proc.wait(10)
                    except (
                        psutil.NoSuchProcess,
                        psutil.TimeoutExpired,
                        psutil.AccessDenied,
                    ):
                        pass
            logger.info("终止进程完成")
        except ImportError:
            logger.warning("psutil模块未安装，跳过进程终止步骤")

    def cover_folder(self):
        """覆盖安装最新版本的文件。"""
        try:
            logger.info("开始覆盖...")
            if not os.path.exists(self.extract_folder_path):
                logger.error(f"解压目录不存在: {self.extract_folder_path}")
                return False

            # 遍历解压目录中的所有文件和文件夹，并复制到工作目录
            for item_name in os.listdir(self.extract_folder_path):
                source_item = os.path.join(self.extract_folder_path, item_name)
                target_item = os.path.join(self.cover_folder_path, item_name)

                if os.path.isdir(source_item):
                    shutil.copytree(source_item, target_item, dirs_exist_ok=True)
                else:
                    shutil.copy2(source_item, target_item)

            logger.info(f"覆盖完成: {self.cover_folder_path}")
            return True
        except Exception as e:
            logger.error(f"覆盖失败: {e}")
            return False

    def cleanup(self):
        """清理下载和解压的临时文件。"""
        logger.info("开始清理...")
        try:
            if os.path.exists(self.temp_path):  # 删除临时目录
                shutil.rmtree(self.temp_path)
                logger.info(f"清理完成: {self.temp_path}")
            if os.path.exists(self.download_file_path):
                os.remove(self.download_file_path)
                logger.info(f"清理完成: {self.download_file_path}")
            if os.path.exists(self.extract_folder_path):
                shutil.rmtree(self.extract_folder_path)
                logger.info(f"清理完成: {self.extract_folder_path}")
        except Exception as e:
            logger.error(f"清理失败: {e}")

    def run(self):
        """运行更新流程。"""
        try:
            # 获取最新版本信息
            self.get_release_info()
            # 比较版本
            if self.compare_versions():
                # 下载文件
                self.download_file()
                # 解压文件
                if self.extract_file():
                    # 终止进程
                    self.terminate_processes()
                    # 覆盖安装
                    if self.cover_folder():
                        # 清理临时文件
                        self.cleanup()
                        return True
            else:
                logger.info("当前已是最新版本，无需更新")
            return False
        except Exception as e:
            logger.error(f"更新过程中出现错误: {e}")
            return False


# 创建API类用于前端交互
class UpdaterApi:
    """API类用于处理前端交互。"""

    def __init__(self):
        self.updater = None
        self.latest_version_info = None

    def check_update(self):
        try:
            updater = Updater()
            updater.get_release_info()

            if (
                "assets" in updater.release_info
                and len(updater.release_info["assets"]) > 0
            ):
                download_url = updater.release_info["assets"][0].get(
                    "browser_download_url", ""
                )
                file_name = download_url.split("/")[-1] if download_url else ""
            elif "browser_download_url" in updater.release_info:
                download_url = updater.release_info["browser_download_url"]
                file_name = download_url.split("/")[-1] if download_url else ""
            else:
                download_url = ""
                file_name = ""

            version = updater.release_info.get("version", "Unknown")

            if download_url and updater.compare_versions():
                self.latest_version_info = {
                    "download_url": download_url,
                    "file_name": file_name,
                    "version": version,
                }
                return {
                    "available": True,
                    "download_url": download_url,
                    "file_name": file_name,
                    "version": version,
                }
            else:
                return {"available": False, "message": "当前已是最新版本"}
        except Exception as e:
            logger.error(f"检查更新时出错: {e}")
            return {"available": False, "error": str(e)}

    def start_update(self, params=None):
        try:
            if params is None:
                params = {}

            download_url = params.get("download_url", "")
            file_name = params.get("file_name", "")

            # 如果没有提供参数，则使用已检查的版本信息
            if (
                not download_url
                and hasattr(self, "latest_version_info")
                and self.latest_version_info
            ):
                download_url = self.latest_version_info.get("download_url", "")
                file_name = self.latest_version_info.get("file_name", "")

            self.updater = Updater()
            # 手动设置下载信息
            if download_url:
                self.updater.release_info = {
                    "browser_download_url": download_url,
                    "version": "latest",
                }
                self.updater.file_name = file_name

            success = self.updater.run()

            if success:
                return {"success": True}
            else:
                return {"success": False, "error": "更新过程失败或无需更新"}
        except Exception as e:
            logger.error(f"开始更新时出错: {e}")
            return {"success": False, "error": str(e)}


def main():
    api = UpdaterApi()

    # 创建webview窗口
    webview.create_window(
        "应用程序更新器",
        html=create_simple_frontend(),
        width=800,
        height=600,
        resizable=True,
        js_api=api,
    )

    # 启动webview
    webview.start(debug=False)


def _main():
    pass


if __name__ == "__main__":
    updater = Updater()

    updater.run()
