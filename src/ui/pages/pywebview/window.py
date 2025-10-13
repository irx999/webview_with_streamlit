import requests
import streamlit as st
from streamlit import session_state as ss


def get_window_size():
    width = requests.get(
        "http://127.0.0.1:48000/api/v1/pywebview/window/get?property=width",
    ).json()["data"]
    height = requests.get(
        "http://127.0.0.1:48000/api/v1/pywebview/window/get?property=height",
    ).json()["data"]

    return int(width), int(height)


def set_window_size() -> None:
    width = ss.get("width", 1200)
    height = ss.get("height", 800)
    requests.post(
        "http://127.0.0.1:48000/api/v1/pywebview/window/set",
        json={"func": "resize", "width": width, "height": height},
    )


def change_window_fullscreen() -> None:
    requests.post(
        "http://127.0.0.1:48000/api/v1/pywebview/window/set",
        json={"func": "toggle_fullscreen"},
    )


def change_on_top() -> None:
    import time

    time.sleep(0.1)
    requests.post(
        "http://127.0.0.1:48000/api/v1/pywebview/window/set",
        json={"func": "on_top"},
    )


if __name__ == "__main__":
    width = st.slider(
        "输入宽度",
        1200,
        2560,
        key="width",
        step=100,
        value=get_window_size()[0],
        on_change=set_window_size,
    )
    height = st.slider(
        "输入高度",
        800,
        1440,
        key="height",
        step=100,
        value=get_window_size()[1],
        on_change=set_window_size,
    )
    st.toggle(
        "切换全屏",
        on_change=change_window_fullscreen,
    )
    st.toggle(
        "切换置顶",
        on_change=change_on_top,
    )
