import multiprocessing
import os
import sys
import threading

import webview


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


def start_streamlit() -> multiprocessing.Process:
    """启动Streamlit服务器"""

    """在单独的线程中启动Streamlit服务器"""
    options = {}
    script_path = get_script_path()
    port = 8501
    options["server.address"] = "localhost"
    options["server.port"] = str(port)
    options["server.headless"] = "true"
    options["global.developmentMode"] = "false"
    # options["client.showErrorDetails"] = "none"
    options["client.toolbarMode"] = "viewer"  # "minimal or viewer"

    multiprocessing.freeze_support()
    streamlit_process = multiprocessing.Process(
        target=run_streamlit,
        args=(script_path, options),
        name="Streamlit_app",
    )
    streamlit_process.start()

    return streamlit_process


def start_fastapi() -> threading.Thread:
    """启动Fastapi服务器"""

    def run():
        import uvicorn

        from src.fast_api.fastapi_app import app

        # 使用导入字符串而不是应用实例，以支持重载功能
        uvicorn.run(
            app,
            host="localhost",
            port=48000,
            log_level="warning",
            # reload=True,
        )

    fastapi_thread = threading.Thread(target=run, daemon=True, name="Fastapi_app")
    fastapi_thread.start()
    return fastapi_thread


def start_webview() -> webview.Window:
    """启动webview服务器"""

    window = webview.create_window(
        "My_app",
        f"http://localhost:{8501}",
        width=1200,
        height=800,
        # min_size=(1200, 800),
        shadow=True,
        on_top=False,
        # x=0,
        # y=0,
    )
    window.name = "webview_app"  # type: ignore #
    webview.start(debug=True)

    return window  # type: ignore
