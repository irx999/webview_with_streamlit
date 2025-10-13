import os
import sys
from typing import Any

import streamlit as st
from streamlit import session_state as ss


def get_script_path() -> str:
    script_path = "src/ui/pages/"
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, script_path)  # type: ignore
    else:
        return os.path.join(os.getcwd(), script_path)


def get_path(path) -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, path)  # type: ignore
    else:
        return os.path.join(os.getcwd(), path)


HP = get_script_path()


def st_sidebar():
    st.sidebar.success(f"**当前登录用户:**   {ss.get('name', '未知用户')}")
    st.sidebar.success(f"**当前登录权限:**   {ss.get('roles', '未知权限')}")

    with st.sidebar.expander("**Cache_Manager**"):
        st.button(
            "⚙️Clear_cache_resource",
            on_click=lambda: st.cache_resource.clear(),
        )
        st.button(
            "⚙️Clear_cache_data",
            on_click=lambda: st.cache_data.clear(),
        )
        st.button(
            "⚙️Delete_cookie",
            # on_click=lambda: authenticator.cookie_controller.delete_cookie(),
        )
    columns = st.sidebar.columns([1, 1], vertical_alignment="center")
    columns[0].image("assets//images/©.png", width=150)
    columns[1].caption(
        "Developed by [irx999](https://github.com/irx999)  \n All rights reserved"
    )


PAGES: dict[str, list[Any]] = {
    "🏠Home": [
        st.Page(
            HP + "Home/welcome.py",
            title="主页",
            icon="🏠",
        ),
    ],
    "功能测试": [
        st.Page(
            HP + "Test/test_a.py",
            title="测试页1",
            icon="🧪",
        ),
        st.Page(
            HP + "Test/test_b.py",
            title="测试页2",
            icon="🧪",
        ),
    ],
    "Pywebview": [
        st.Page(
            HP + "pywebview/window.py",
            title="window",
            icon="🧪",
        ),
    ],
}
