import json
import os
import shutil
import subprocess

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
        # 这里需要修改
        self.process_names = [
            "March7th Assistant.exe",
            "March7th Launcher.exe",
            "flet.exe",
            "gui.exe",
        ]
        self.api_urls = [
            "https://api.github.com/repos/moesnow/March7thAssistant/releases/latest",
        ]
        self.temp_path = os.path.abspath("./temp")
        os.makedirs(self.temp_path, exist_ok=True)

        self.file_name = ""

        self.download_file_path = os.path.join(self.temp_path, self.file_name)
        self.extract_folder_path = os.path.join(
            self.temp_path, self.file_name.rsplit(".", 1)[0]
        )

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
        if os.path.exists("./assets/lastest.json"):
            with open("./assets/lastest.json", "r", encoding="utf-8") as file:
                return json.load(file)["version"]
        logger.error("❌ 本地信息不存在 将返回0.0.0")
        return "0.0.0"

    def compare_versions(self):
        """处理发布数据，获取下载URL并比较版本。"""
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
            url = self.release_info["download_url"]
            with requests.get(url) as response:
                with open(self.download_file_path, "wb") as file:
                    file.write(response.content)
        except Exception as e:
            logger.error(f"下载失败: {e}")
            input("按回车键重新下载. . .")
            if os.path.exists(self.download_file_path):
                os.remove(self.download_file_path)

    def extract_file(self):
        """解压下载的文件。"""
        while True:
            try:
                logger.info("🌟 开始解压...")
                if os.path.exists(self.exe_path):
                    subprocess.run(
                        [
                            self.exe_path,
                            "x",
                            self.download_file_path,
                            f"-o{self.temp_path}",
                            "-aoa",
                        ],
                        check=True,
                    )
                else:
                    shutil.unpack_archive(self.download_file_path, self.temp_path)
                logger.info(f"解压完成: {self.extract_folder_path}")
                return True
            except Exception as e:
                logger.error(f"解压失败: {e}")
                input("按回车键重新下载. . .")
                if os.path.exists(self.download_file_path):
                    os.remove(self.download_file_path)
                return False

    def cover_folder(self):
        """覆盖安装最新版本的文件。"""
        try:
            logger.info("开始覆盖...")
            if "full" in self.file_name and os.path.exists(self.delete_folder_path):
                shutil.rmtree(self.delete_folder_path)
            shutil.copytree(
                self.extract_folder_path, self.cover_folder_path, dirs_exist_ok=True
            )
            logger.info(f"覆盖完成: {green(self.cover_folder_path)}")
            break
        except Exception as e:
            logger.error(f"覆盖失败: {red(e)}")

    def terminate_processes(self):
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

    def cleanup(self):
        """清理下载和解压的临时文件。"""
        logger.info("开始清理...")
        try:
            os.remove(self.download_file_path)
            logger.info(f"清理完成: {self.download_file_path}")
            shutil.rmtree(self.extract_folder_path)
            logger.info(f"清理完成: {self.extract_folder_path}")
        except Exception as e:
            logger.error(f"清理失败: {e}")

    def run(self):
        """运行更新流程。"""
        try:
            self.extract_file()
            self.terminate_processes()
            self.cover_folder()
            self.cleanup()
            return True
        except Exception as e:
            logger.error(f"更新过程中出现错误: {e}")
            return False


# 创建API类用于前端交互
class UpdaterApi:
    def __init__(self):
        self.updater = None
        self.latest_version_info = None

    def check_update(self):
        try:
            updater = Updater(logger)
            download_url, version = updater.get_download_url()
            self.latest_version_info = {
                "download_url": download_url,
                "file_name": updater.file_name,
                "version": version,
            }
            return {
                "available": True,
                "download_url": download_url,
                "file_name": updater.file_name,
                "version": version,
            }
        except Exception as e:
            logger.error(f"检查更新时出错: {e}")
            return {"available": False, "error": str(e)}

    def start_update(self, params):
        try:
            download_url = params.get("download_url")
            file_name = params.get("file_name")

            self.updater = Updater(logger, download_url, file_name)
            success = self.updater.run()

            if success:
                return {"success": True}
            else:
                return {"success": False, "error": "更新过程失败"}
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


if __name__ == "__main__":
    main()
