import streamlit as st

# from streamlit import session_state as ss
from src.app import App
from src.ui.window import window_setting

# from streamlit_cookies_controller import CookieController

# controller = CookieController(key="cookies")


def st_sidebar():
    # if ss.get("name", None) is None:
    #     st.sidebar.error("**当前登录用户:** 未知")
    # else:
    #     st.sidebar.success(f"**当前登录用户:**   {ss.get('name', '未知用户')}")
    # if ss.get("roles", None) is None:
    #     st.sidebar.error("**当前登录权限:** 未知")
    # else:
    #     st.sidebar.success(f"**当前登录权限:**   {ss.get('roles', '未知权限')}")
    #  窗口调节
    with st.sidebar.container(border=True):
        window_setting()

    # 版权信息
    columns = st.sidebar.columns([1, 1], vertical_alignment="center")
    columns[0].image("assets//images/©.png", width=150)
    columns[1].caption(
        "Developed by [irx999](https://github.com/irx999)  \n All rights reserved"
    )

    st.sidebar.badge(App.name + " -> " + App.version, icon="📦", color="green")
    st.sidebar.badge("v->" + str(App.latestinfo["version"]), icon="🏷️", color="violet")
    st.sidebar.badge("t->" + App.mtime, icon="🏷️", color="blue")

    st.sidebar.caption(App.description)

    with st.sidebar.popover("Modules_Info"):
        for k, v in App.hidden_import.items():
            st.badge(f"{k} -> {v}", icon="📦")

    with st.sidebar.popover("Cache_Manager"):
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
            # on_click=lambda: controller.remove("cookies"),
        )
