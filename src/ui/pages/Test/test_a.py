import os
import sys

import requests
import streamlit as st


def get_path(path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, path)  # type: ignore
    return os.path.join(os.getcwd(), path)


path_to_dat = get_path("assets/images.png")
if __name__ == "__main__":
    width = st.slider("输入宽度", 800, 5000)
    height = st.slider("输入高度", 600, 5000)
    requests.get(
        f"http://127.0.0.1:8000/api/v1/pywebview/window/resize?width={width}&height={height}"
    )
    st.image(path_to_dat)

    st.image("assets/images.png")
