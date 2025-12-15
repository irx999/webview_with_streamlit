import requests
import streamlit as st
from streamlit import session_state as ss

from src.app.app_info import App_fastapi


def get_window_size():
    try:
        width_response = requests.get(
            f"{App_fastapi.base_url}/pywebview/window/get?property=width",
            timeout=5,
        )
        width_data = width_response.json()
        width = width_data["data"]

        height_response = requests.get(
            f"{App_fastapi.base_url}/pywebview/window/get?property=height",
            timeout=5,
        )
        height_data = height_response.json()
        height = height_data["data"]

        return int(width), int(height)
    except Exception as e:
        st.toast(f"获取窗口尺寸时发生错误: {e}", icon="error")
        # 发生任何异常时返回默认尺寸
        return 1200, 800


def set_window_size() -> None:
    try:
        width = ss.get("windows_width", 1200)
        height = ss.get("windows_height", 800)
        response = requests.post(
            f"{App_fastapi.base_url}/pywebview/window/set",
            json={"func": "resize", "width": width, "height": height},
            timeout=5,
        )
        result = response.json()
        if result.get("status") != "success":
            st.toast(f"窗口调整失败: {result.get('data', '未知错误')}")
    except Exception as e:
        st.toast(f"设置窗口尺寸时发生错误: {e}")


def change_window_fullscreen() -> None:
    try:
        response = requests.post(
            f"{App_fastapi.base_url}/pywebview/window/set",
            json={"func": "toggle_fullscreen"},
            timeout=5,
        )
        result = response.json()
        if result.get("status") != "success":
            st.toast(f"全屏切换失败: {result.get('data', '未知错误')}")
        else:
            st.toast("✅ 窗口全屏状态已切换")
    except Exception as e:
        st.toast(f"切换全屏时发生错误: {e}")


def change_on_top() -> None:
    try:
        import time

        time.sleep(0.1)
        response = requests.post(
            f"{App_fastapi.base_url}/pywebview/window/set",
            json={"func": "on_top"},
            timeout=5,
        )
        result = response.json()
        if result.get("status") != "success":
            st.toast(f"窗口置顶失败: {result.get('data', '未知错误')}")
        else:
            st.toast("✅ 窗口置顶状态已切换")
    except Exception as e:
        st.toast(f"切换窗口置顶时发生错误: {e}")


if __name__ == "__main__":
    windows_width, windows_height = get_window_size()
    width = st.slider(
        "输入宽度",
        1200,
        2560,
        key="windows_width",
        step=100,
        value=windows_width,
        on_change=set_window_size,
    )
    height = st.slider(
        "输入高度",
        800,
        1440,
        key="windows_height",
        step=100,
        value=windows_height,
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
