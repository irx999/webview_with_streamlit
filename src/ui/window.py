import time
from typing import Any

import requests
import streamlit as st
from streamlit import session_state as ss

from src.app.app_info import App_fastapi


def _call_window_api(
    method: str,
    path: str,
    *,
    params: dict | None = None,
    json_body: dict | None = None,
    error_prefix: str = "调用窗口 API 失败",
) -> dict | None:
    """统一调用 FastAPI 的 /pywebview/window/* 接口。

    返回成功时的响应 dict（含 status/data），失败时返回 None 并 toast。
    """
    url = f"{App_fastapi.base_url}{path}"
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=1)
        else:
            response = requests.post(url, json=json_body, timeout=1)
        result = response.json()
    except Exception as e:
        st.toast(f"{error_prefix}: {e}", icon="❌")
        return None

    if result.get("status") != "success":
        st.toast(result.get("data", "错误"), icon="❌")
        return None
    return result


def _get_window_property(prop: str) -> Any | None:
    result = _call_window_api(
        "GET",
        "/pywebview/window/get",
        params={"property": prop},
        error_prefix=f"获取窗口属性 {prop} 失败",
    )
    return result["data"] if result else None


def get_window_size() -> tuple[int, int]:
    width = _get_window_property("width")
    height = _get_window_property("height")
    if width is None or height is None:
        return 1200, 800
    return int(width), int(height)


def set_window_size() -> None:
    result = _call_window_api(
        "POST",
        "/pywebview/window/set",
        json_body={
            "func": "resize",
            "width": ss.get("windows_width", 1200),
            "height": ss.get("windows_height", 800),
        },
        error_prefix="设置窗口尺寸时发生错误",
    )
    if result:
        st.toast("窗口尺寸已调整", icon="✅")


def change_window_fullscreen() -> None:
    time.sleep(0.1)
    result = _call_window_api(
        "POST",
        "/pywebview/window/set",
        json_body={"func": "toggle_fullscreen"},
        error_prefix="切换全屏时发生错误",
    )
    if result:
        st.toast("窗口全屏状态已切换", icon="✅")
    ss["windows_fullscreen"] = ss.get("windows_fullscreen", True)


def change_on_top() -> None:
    time.sleep(0.1)
    result = _call_window_api(
        "POST",
        "/pywebview/window/set",
        json_body={"func": "on_top"},
        error_prefix="切换窗口置顶时发生错误",
    )
    if result:
        st.toast("窗口置顶状态已切换", icon="✅")
    ss["windows_on_top"] = ss.get("windows_on_top", True)


def window_setting():
    st.badge("窗口设置", icon="⚙️")

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
        on_change=set_window_size,
    )
    c1[1].slider(
        "windows_h",
        800,
        1440,
        key="windows_height",
        step=100,
        on_change=set_window_size,
    )

    # 窗口状态
    with st.container(horizontal=True):
        st.toggle(
            "全屏",
            on_change=change_window_fullscreen,
            key="windows_fullscreen",
        )
        st.space("stretch")
        st.toggle(
            "置顶",
            key="windows_on_top",
            on_change=change_on_top,
        )
        st.space("stretch")


if __name__ == "__main__":
    window_setting()
