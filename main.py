import os
import sys

from loguru import logger

from src.app import start_fastapi, start_streamlit, start_webview

logger.add("logs/main.log", format="{time} {level} {message}")


def main():
    try:
        logger.info("🌟 Starting...")
        streamlit_app = start_streamlit()
        start_fastapi()
        start_webview()
    except Exception as e:
        logger.exception(e)
    finally:
        logger.info("🌟 Stoping...")
        streamlit_app.terminate()
        streamlit_app.join()


if __name__ == "__main__":
    if getattr(sys, "frozen", False):
        sys.path.append(os.path.dirname(sys.executable))
        # 原来的方案
        main_working_dir = getattr(sys, "_MEIPASS", os.path.abspath(__file__))
        # 现在的方案
        main_working_dir = os.path.dirname(sys.executable)
        logger.info(f"🌟 Runing in {main_working_dir} by fozen")
        os.chdir(main_working_dir)

    main()
