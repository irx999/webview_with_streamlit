import argparse
import os
import sys

import webview
from loguru import logger

from src.app import start_fastapi, start_streamlit, start_webview

logger.add("logs/app.log", format="{time} {level} {message}")


def main(debug_mode: bool = False):
    try:
        streamlit_app = start_streamlit(debug_mode)
        logger.info(f"✅ Start succes -> {streamlit_app.name}")

        fastapi_app = start_fastapi(debug_mode)
        logger.info(f"✅ Start succes -> {fastapi_app.name}")

        webview_app = start_webview(debug_mode)
        logger.info(f"✅ Start succes -> {webview_app.name}")  # type: ignore #

        logger.info(f"🌟 Starting -> {webview.__name__}")

        # 这里好像不需要这个东西
        # webview.start()

    except Exception as e:
        logger.exception(e)
    finally:
        logger.info("🌟 Stoping...")

        streamlit_app.terminate()
        streamlit_app.join()
        webview_app.destroy()

        logger.info("✅ Stoped")
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

        main()
    else:
        logger.info(f"🌟 Runing in {os.getcwd()} by uv")

        parser = argparse.ArgumentParser(description="Webview Application")
        parser.add_argument(
            "--debug", "-d", action="store_true", help="Enable debug mode"
        )
        parser.add_argument(
            "--start", "-s", type=str, help="Start the app with password"
        )

        args = parser.parse_args()

        if args.debug:
            logger.debug("🐛 Debug mode enabled")

        if not args.start or args.start != "123":
            logger.error("🔑 Invalid password")
            sys.exit(0)

        main(
            debug_mode=args.debug,
        )
