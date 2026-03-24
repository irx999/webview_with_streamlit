import argparse
import os
import sys

from loguru import logger

from src.app import (
    init,
    start_fastapi,
    start_streamlit,
    start_webview,
)

logger.add("logs/app.log", format="{time} {level} {message}")


def main(debug_mode: bool = False):
    # 初始化应用实例变量，防止 finally 块引用未定义变量
    streamlit_app = None
    webview_app = None
    fastapi_app = None

    try:
        # 启动 streamlit
        streamlit_app = start_streamlit(debug_mode)
        logger.info(f"Start success -> {streamlit_app.name}")

        # 启动 fastapi
        fastapi_app = start_fastapi(debug_mode)
        logger.info(f"Start success -> {fastapi_app.name}")

        # 启动 webview
        webview_app = start_webview(debug_mode)

    except Exception as e:
        logger.exception(f"Application startup failed: {e}")
    finally:
        logger.info("Stopping...")

        if streamlit_app is not None:
            try:
                streamlit_app.terminate()
                streamlit_app.join()
            except Exception as e:
                logger.error(f"Error stopping streamlit app: {e}")

        if webview_app is not None:
            try:
                webview_app.destroy()
            except Exception as e:
                logger.error(f"Error destroying webview app: {e}")

        logger.info("Stopped")
        # 仅在非正常退出或需要明确退出码时调用，正常流程可由主线程结束自然退出
        # 但为了保持原有逻辑，保留此处
        sys.exit()


if __name__ == "__main__":
    # 检查单实例
    if getattr(sys, "frozen", False):
        sys.path.append(os.path.dirname(sys.executable))
        # 原来的方案
        # main_working_dir = getattr(sys, "_MEIPASS", os.path.abspath(__file__))
        # 现在的方案
        main_working_dir = os.path.dirname(sys.executable)
        logger.info(f"Running in {main_working_dir} by frozen")
        # 切换工作目录
        os.chdir(main_working_dir)

        # 初始化
        init()

        # 启动
        main()
    else:
        logger.info(f"Running in {os.getcwd()} by uv")

        parser = argparse.ArgumentParser(description="Webview Application")
        parser.add_argument(
            "--debug", "-d", action="store_true", help="Enable debug mode"
        )
        parser.add_argument(
            "--start", "-s", type=str, help="Start the app with password"
        )

        args = parser.parse_args()

        if args.debug:
            logger.debug("Debug mode enabled")

        if not args.start or args.start != "123":
            logger.warning("Invalid password")
            sys.exit(0)
        # 启动
        main(
            debug_mode=args.debug,
        )
