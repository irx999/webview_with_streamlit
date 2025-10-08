from src.app import start_fastapi, start_streamlit, start_webview


def main():
    try:
        streamlit_app = start_streamlit()
        start_fastapi()
        start_webview()
    finally:
        streamlit_app.terminate()
        streamlit_app.join()


if __name__ == "__main__":
    main()
