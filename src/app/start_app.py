import multiprocessing
import os
import sys
import threading

import webview

from .app_info import App, App_fastapi, App_streamlit


def get_script_path() -> str:
    script_path = "src/ui/streamlit_app.py"
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, script_path)  # type: ignore
    else:
        return os.path.join(os.getcwd(), script_path)


def run_streamlit(script_path: str, options) -> None:
    from streamlit.web import cli as stcli

    """启动Streamlit服务器"""
    args = ["streamlit", "run", script_path]
    args.extend([f"--{key}={value}" for key, value in options.items()])
    sys.argv = args
    stcli.main()


def start_streamlit(debug_mode: bool = False) -> multiprocessing.Process:
    """启动Streamlit服务器"""

    """在单独的线程中启动Streamlit服务器"""
    options = {}
    script_path = get_script_path()
    port = App_streamlit.port

    options["server.address"] = App_streamlit.host
    options["server.port"] = str(port)
    options["server.headless"] = "true"  # 关掉了就会打开一个浏览器
    options["global.developmentMode"] = "false"  # 这个必须参数都为false
    # options["client.showErrorDetails"] = "none"
    options["client.toolbarMode"] = "minimal"  # "minimal or viewer"

    multiprocessing.freeze_support()
    process = multiprocessing.Process(
        target=run_streamlit,
        args=(script_path, options),
        name="Streamlit_app",
    )
    process.start()

    return process


def run_fastapi():
    import uvicorn

    from src.fast_api.fastapi_app import app

    # 使用导入字符串而不是应用实例，以支持重载功能
    uvicorn.run(
        app=app,
        # app="src.fast_api.fastapi_app:app",
        host=App_fastapi.host,
        port=App_fastapi.port,
        log_level="warning",
        # reload=True,
    )


def start_fastapi(debug_mode: bool = False) -> threading.Thread:
    """启动Fastapi服务器"""

    thread = threading.Thread(
        target=run_fastapi,
        daemon=True,
        name=App_fastapi.name,
    )
    thread.start()
    return thread


def start_webview(debug_mode: bool = False) -> webview.Window:
    """启动webview服务器"""

    window = webview.create_window(
        App.name,
        App_streamlit.base_url,
        width=1200,
        height=800,
        resizable=False,
        min_size=(1200, 800),
        shadow=True,
        on_top=False,
        transparent=True,
        # frameless=True,
        # x=0,
        # y=0,
    )
    window.name = App.name  # type: ignore #
    webview.start(
        debug=debug_mode,
        icon="assets/ico/app.ico",
    )

    return window  # type: ignore
