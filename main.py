import multiprocessing
import os
import sys

import webview
from streamlit.web import cli as stcli


def get_script_path():
    script_path = "streamlit_app.py"
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, os.path.basename(script_path))  # type: ignore
    else:
        return os.path.join(
            os.path.dirname(sys.executable), os.path.basename(script_path)
        )


def run_streamlit(script_path: str, options):
    args = ["streamlit", "run", script_path]
    args.extend([f"--{key}={value}" for key, value in options.items()])
    sys.argv = args
    stcli.main()


def main():
    # 在单独的线程中启动Streamlit服务器
    options = {}
    script_path = get_script_path()
    port = 8501
    options["server.address"] = "localhost"
    options["server.port"] = str(port)
    options["server.headless"] = "true"
    options["global.developmentMode"] = "false"

    multiprocessing.freeze_support()
    streamlit_process = multiprocessing.Process(
        target=run_streamlit, args=(script_path, options)
    )
    streamlit_process.start()

    try:
        webview.create_window("title", "http://localhost:8501", width=1200, height=800)
        webview.start()
    finally:
        # Ensure the Streamlit process is terminated
        streamlit_process.terminate()
        streamlit_process.join()


if __name__ == "__main__":
    main()
