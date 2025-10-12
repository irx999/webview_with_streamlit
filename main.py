import os
import sys

import webview
from loguru import logger

from src.app import start_fastapi, start_streamlit, start_webview

logger.add("logs/app.log", format="{time} {level} {message}")


def main():
    try:
        streamlit_app = start_streamlit()
        logger.info(f"✅ Start succes -> {streamlit_app.name}")

        fastapi_app = start_fastapi()
        logger.info(f"✅ Start succes -> {fastapi_app.name}")

        webview_app = start_webview()
        logger.info(f"✅ Start succes -> {webview_app.title}")

        logger.info(f"🌟 Starting -> {webview.__name__}")
        webview.start()

    except Exception as e:
        logger.exception(e)
    finally:
        logger.info("🌟 Stoping...")

        streamlit_app.terminate()
        streamlit_app.join()

        fastapi_app.join()

        webview_app.destroy()
        sys.exit()


if __name__ == "__main__":
    if getattr(sys, "frozen", False):
        sys.path.append(os.path.dirname(sys.executable))
        # 原来的方案
        main_working_dir = getattr(sys, "_MEIPASS", os.path.abspath(__file__))
        # 现在的方案
        main_working_dir = os.path.dirname(sys.executable)
        os.chdir(main_working_dir)

        logger.info(f"🌟 Runing in {main_working_dir} by fozen")
    else:
        logger.info(f"🌟 Runing in {os.getcwd()} by uv")

    main()
