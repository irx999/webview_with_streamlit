import streamlit as st
from streamlit import session_state as ss
from streamlit_cookies_controller import CookieController

controller = CookieController(key="cookies")


def st_sidebar():
    if ss.get("name", None) is None:
        st.sidebar.error("**当前登录用户:** 未知")
    else:
        st.sidebar.success(f"**当前登录用户:**   {ss.get('name', '未知用户')}")
    if ss.get("roles", None) is None:
        st.sidebar.error("**当前登录权限:** 未知")
    else:
        st.sidebar.success(f"**当前登录权限:**   {ss.get('roles', '未知权限')}")

    with st.sidebar.expander("**Cache_Manager**"):
        st.button(
            "⚙️Clear_cache_res",
            on_click=lambda: st.cache_resource.clear(),
        )
        st.button(
            "⚙️Clear_cache_data",
            on_click=lambda: st.cache_data.clear(),
        )
        st.button(
            "⚙️Delete_cookie",
            # on_click=lambda: authenticator.cookie_controller.delete_cookie(),
            on_click=lambda: controller.remove("cookies"),
        )
    columns = st.sidebar.columns([1, 1], vertical_alignment="center")
    columns[0].image("assets//images/©.png", width=150)
    columns[1].caption(
        "Developed by [irx999](https://github.com/irx999)  \n All rights reserved"
    )
