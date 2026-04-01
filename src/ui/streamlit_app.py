import streamlit as st

from src.ui.pages import PAGES
from src.ui.sidebar import st_sidebar

st.set_page_config(
    page_title="My App",
    layout="wide",
    page_icon="🧊",
    initial_sidebar_state="auto",
    # menu_items={
    #     "About": "# This is a header. This is an *extremely* cool app!",
    # },
)

st.logo(
    # image="https://irx999.fun/img/tx1.jpg",
    image="http://irx999.fun/img/QVQ.gif",
    link="https://github.com/irx999",
    icon_image="http://irx999.fun/img/QVQ.gif",
)


def main():
    # 侧边栏
    st_sidebar()
    pg = st.navigation(pages=PAGES, position="top", expanded=True)
    pg.run()


if __name__ == "__main__":
    main()
