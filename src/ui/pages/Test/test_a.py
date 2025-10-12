import requests
import streamlit as st

if __name__ == "__main__":
    width = st.slider("输入宽度", 800, 5000)
    height = st.slider("输入高度", 600, 5000)
    requests.get(
        f"http://127.0.0.1:8000/api/v1/pywebview/window/resize?width={width}&height={height}"
    )
