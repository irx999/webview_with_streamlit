import os
import sys

from loguru import logger

from src.app import start_fastapi, start_streamlit, start_webview

logger.add("logs/log.log", format="{time} {level} {message}")


def main():
    try:
        streamlit_app = start_streamlit()
        start_fastapi()
        start_webview()
    finally:
        streamlit_app.terminate()
        streamlit_app.join()


if __name__ == "__main__":
    if getattr(sys, "frozen", False):
        sys.path.append(os.path.dirname(sys.executable))
        # 原来的方案
        main_working_dir = getattr(sys, "_MEIPASS", os.path.abspath(__file__))
        # 现在的方案
        main_working_dir = os.path.dirname(sys.executable)
        os.chdir(main_working_dir)

    main()
