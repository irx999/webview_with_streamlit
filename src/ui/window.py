import requests
import streamlit as st
from streamlit import session_state as ss

from src.app.app_info import App_fastapi


def get_window_size():
    try:
        width_response = requests.get(
            f"{App_fastapi.base_url}/pywebview/window/get?property=width",
            timeout=1,
        )
        width_data = width_response.json()
        width = width_data["data"]

        height_response = requests.get(
            f"{App_fastapi.base_url}/pywebview/window/get?property=height",
            timeout=1,
        )
        height_data = height_response.json()
        height = height_data["data"]

        return int(width), int(height)
    except Exception as e:
        st.toast(f"获取窗口尺寸时发生错误: {e}", icon="❌")
        # 发生任何异常时返回默认尺寸
        return 1200, 800


def set_window_size() -> None:
    try:
        width = ss.get("windows_width", 1200)
        height = ss.get("windows_height", 800)
        response = requests.post(
            f"{App_fastapi.base_url}/pywebview/window/set",
            json={"func": "resize", "width": width, "height": height},
            timeout=1,
        )
        result = response.json()
        if result.get("status") == "success":
            st.toast("窗口尺寸已调整", icon="✅")
        else:
            st.toast(result.get("data", "错误"), icon="❌")
    except Exception as e:
        st.toast(f"设置窗口尺寸时发生错误: {e}", icon="❌")


def change_window_fullscreen() -> None:
    try:
        import time

        time.sleep(0.1)
        response = requests.post(
            f"{App_fastapi.base_url}/pywebview/window/set",
            json={"func": "toggle_fullscreen"},
            timeout=1,
        )
        result = response.json()
        if result.get("status") == "success":
            st.toast("窗口全屏状态已切换", icon="✅")

        else:
            st.toast(result.get("data", "错误"), icon="❌")

        ss["windows_fullscreen"] = ss.get("windows_fullscreen", True)

    except Exception as e:
        st.toast(f"切换全屏时发生错误: {e}", icon="❌")


def change_on_top() -> None:
    try:
        import time

        time.sleep(0.1)
        response = requests.post(
            f"{App_fastapi.base_url}/pywebview/window/set",
            json={"func": "on_top"},
            timeout=1,
        )
        result = response.json()
        if result.get("status") == "success":
            st.toast("窗口置顶状态已切换", icon="✅")
        else:
            st.toast(result.get("data", "错误"), icon="❌")
        ss["windows_on_top"] = ss.get("windows_on_top", True)

    except Exception as e:
        st.toast(f"切换窗口置顶时发生错误: {e}", icon="❌")


def window_setting():
    st.badge("窗口设置", icon="⚙️")
    # st.subheader("窗口尺寸")

    # 窗口尺寸
    c1 = st.columns(2)
    windows_width, windows_height = get_window_size()
    ss["windows_width"] = windows_width
    ss["windows_height"] = windows_height
    c1[0].slider(
        "windows_w",
        1200,
        2560,
        key="windows_width",
        step=100,
        # value=windows_width,
        on_change=set_window_size,
    )
    c1[1].slider(
        "windows_h",
        800,
        1440,
        key="windows_height",
        step=100,
        # value=windows_height,
        on_change=set_window_size,
    )

    # 窗口状态
    c2 = st.columns(2)
    c2[0].toggle(
        "全屏",
        on_change=change_window_fullscreen,
        key="windows_fullscreen",
    )
    c2[1].toggle(
        "置顶",
        key="windows_on_top",
        on_change=change_on_top,
    )


if __name__ == "__main__":
    window_setting()
