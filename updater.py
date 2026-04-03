import json
import os
import shutil
import subprocess
import threading

import requests
import webview
from loguru import logger

# 配置日志
logger.remove()
logger.add("logs/updater.log", format="{time} {level} {message}", rotation="10 MB")


def create_modern_ui():
    """创建现代化UI界面"""
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>应用程序更新器</title>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            /* 移除所有滚动条 */
            body {
                font-family: 'Noto Sans SC', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #ffffff;
                width: 600px;
                height: 250px;
                overflow: hidden; /* 禁止滚动 */
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 0;
                margin: 0;
            }
            
            .container {
                background: #ffffff;
                width: 600px;
                height: 250px;
                overflow: hidden;
                display: flex;
                position: relative;
            }
            
            .logo-section {
                flex: 0 0 40%; /* 40% 宽度 */
                height: 100%;
                display: flex;
                align-items: center; /* 垂直居中 - 这会让logo在282px高度的中间，即141px位置 */
                justify-content: center; /* 水平居中在40%区域内 */
                position: relative;
            }
            
            .logo-section img {
                max-width: 120px;
                max-height: 120px;
                width: auto;
                height: auto;
                object-fit: contain;
                /* 确保图片本身不会影响居中 */
                display: block;
            }
            
            .progress-section {
                flex: 0 0 60%; /* 60% 宽度 */
                padding: 24px 20px;
                display: flex;
                flex-direction: column;
                gap: 12px;
                height: 100%;
                box-sizing: border-box;
                justify-content: center;
            }
            
            .header {
                color: #2d3748;
                text-align: left;
            }
            
            .header h1 {
                font-size: 20px;
                font-weight: 600;
                margin-bottom: 6px;
                letter-spacing: -0.2px;
            }
            
            .header p {
                color: #718096;
                font-size: 13px;
                line-height: 1.4;
                font-weight: 400;
            }
            
            .status {
                text-align: left;
                font-size: 12px;
                font-weight: 500;
                color: #4a5568;
                min-height: 16px;
                margin-top: 4px;
            }
            
            .loading-icon {
                width: 24px;
                height: 24px;
                border: 2px solid #e2e8f0;
                border-top: 2px solid #4facfe;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 8px 0;
                display: none;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .btn {
                padding: 8px 16px;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-family: 'Noto Sans SC', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            .btn-primary {
                background: #4facfe;
                color: white;
                box-shadow: 0 2px 6px rgba(79, 172, 254, 0.3);
            }
            
            .btn-primary:hover:not(:disabled) {
                background: #3a9bef;
                transform: translateY(-1px);
                box-shadow: 0 3px 8px rgba(79, 172, 254, 0.4);
            }
            
            .btn-primary:disabled {
                background: #e2e8f0;
                color: #a0aec0;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
            
            .btn-secondary {
                background: #f7fafc;
                color: #4a5568;
                border: 1px solid #e2e8f0;
            }
            
            .btn-secondary:hover {
                background: #edf2f7;
                border-color: #cbd5e0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo-section">
                <img src="https://irx999.fun/img/assets/Better-Tools/image/updater.png" alt="Better-tools Logo">
            </div>
            <div class="progress-section">
                <div class="header">
                    <h1>Better-Tools</h1>
                    <p>WebView with Streamlit Desktop Application</p>
                </div>
                <div class="status" id="status">准备就绪</div>
                <div class="loading-icon" id="loading-icon"></div>
                <div class="buttons">
                    <button class="btn btn-primary" id="updateBtn" onclick="startUpdate()">检测更新</button>
                    <button class="btn btn-primary" id="launchBtn" onclick="launchApp()" >启动主程序</button>
                    <button class="btn btn-primary" id="test" onclick="test()" >测试</button>
                </div>
            </div>
        </div>

        <script>
            let updateCompleted = false;
            let isProcessing = false;

            function showLoading() {
                document.getElementById('loading-icon').style.display = 'block';
            }

            function hideLoading() {
                document.getElementById('loading-icon').style.display = 'none';
            }

            function updateUI() {
                pywebview.api.get_status().then(status => {
                    document.getElementById('status').textContent = status.current_status;

                    // 检查是否在处理中
                    isProcessing = status.current_status !== '准备就绪' && 
                                 !status.current_status.includes('更新完成') && 
                                 status.current_status !== '已是最新版本';

                    if (isProcessing) {
                        showLoading();
                    } else {
                        hideLoading();
                    }

                    // 如果更新完成，显示启动按钮
                    if (status.current_status.includes('更新完成') || status.current_status === '已是最新版本') {
                        updateCompleted = true;
                        document.getElementById('updateBtn').style.display = 'none';
                        document.getElementById('launchBtn').style.display = 'inline-flex';
                        hideLoading();
                    }

                    // 更新按钮状态
                    document.getElementById('updateBtn').disabled = isProcessing;
                });
            }

            function startUpdate() {
                document.getElementById('updateBtn').disabled = true;
                showLoading();
                pywebview.api.check_and_update().then(() => {
                    // 开始轮询更新状态
                    const interval = setInterval(() => {
                        updateUI();
                        if (updateCompleted || !isProcessing) {
                            clearInterval(interval);
                        }
                    }, 500);
                });
            }

            function launchApp() {
                pywebview.api.launch_app().then(result => {
                    if (result.success) {
                        setTimeout(() => {
                            window.close();
                        }, 1000);
                    }
                });
            }
            function test() {
            // 2. 调用 Python 的 test 函数
            // 注意：这里假设你已经在 Python 端暴露了 api
            pywebview.api.test().then(result => {
                
                // 3. 判断返回结果是否成功
                if (result.success) {
                    const btn = document.getElementById('updateBtn');
                    
                    // --- 第一步：隐藏按钮 ---
                    btn.style.display = 'none'; 
                    console.log("按钮已隐藏");

                    // --- 第二步：设置定时器，1秒后显示 ---
                    setTimeout(() => {
                        btn.style.display = 'inline-block'; // 或者 'block'，取决于你的布局
                        console.log("按钮已显示");
                    }, 1000); // 1000毫秒 = 1秒
                }
            });
        }

            // 初始化
            document.addEventListener('DOMContentLoaded', () => {
                updateUI();
                setInterval(updateUI, 1000);
            });
        </script>
    </body>
    </html>
    """
    return html_content


class UpdateManager:
    """现代化更新管理器"""

    def __init__(self):
        self.api_urls = [
            "https://d.irx999.fun:2333/index.php?action=download&file=%E6%B5%8B%E8%AF%95%2Flatest.json",
        ]
        self.temp_dir = "./temp"
        os.makedirs(self.temp_dir, exist_ok=True)
        self.download_path = os.path.join(self.temp_dir, "update.zip")
        self.extract_path = os.path.join(self.temp_dir, "extracted")
        self.main_exe_name = "My_app.exe"  # 主程序名称
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
                return True
            else:
                logger.error("主程序不存在")
                return False
        except Exception as e:
            logger.error(f"启动主程序失败: {e}")
            return False


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
        success = self.update_manager.start_main_app()
        return {"success": success}

    def test(self):
        """测试"""
        print("测试")
        return {"success": True}


def main():
    """主函数"""
    api = UpdaterAPI()

    # 创建窗口
    window = webview.create_window(
        "Better-Tools 更新程序",
        html=create_modern_ui(),
        width=600,
        height=300,
        resizable=False,
        js_api=api,
        frameless=False,
    )
    setattr(window, "name", "updater")
    # 启动应用
    webview.start(debug=True)


if __name__ == "__main__":
    main()
