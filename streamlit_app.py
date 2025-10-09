import sys

import streamlit as st

from src.ui.pages import PAGES, st_sidebar

st.set_page_config(page_title="ERP-ext", layout="wide", page_icon="🧊")

st.logo(
    image="https://irx999.fun/img/tx1.jpg",
    link="https://irx999.fun/",
    # icon_image="https://irx999.fun/img/tx1.jpg",
)


def main():
    # 侧边栏
    st_sidebar()
    pg = st.navigation(pages=PAGES, position="top", expanded=True)
    pg.run()

    print("可执行文件路径", sys.executable)


if __name__ == "__main__":
    main()
