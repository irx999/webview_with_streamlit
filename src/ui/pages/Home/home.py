import streamlit as st

from src.app import App


@st.fragment(run_every="2s")
def _banner_carousel() -> None:
    image_list = [
        "./assets/images/Banner3-large-cn.png",
        f"https://placehold.co/790x300/4CAF50/white?text={App.name}",
        f"https://placehold.co/790x300/2196F3/white?text={App.version}",
        f"https://placehold.co/790x300/FF9800/white?text={App.mtime}",
    ]
    idx = st.session_state.get("home_banner_idx", 0)
    st.image(image_list[idx % len(image_list)], link="https://github.com/irx999")
    st.session_state["home_banner_idx"] = idx + 1


if __name__ == "__main__":
    st.container(height=200, border=False)

    with st.container(border=False, horizontal=True):
        st.space("stretch")

        with st.container(
            border=False,
            vertical_alignment="bottom",
            horizontal_alignment="left",
            width=400,
        ):
            _banner_carousel()

            # 三个公告tabs
            tab1, tab2, tab3, tab4 = st.tabs(["None", "None", "None", "None"])

            with tab1:
                st.markdown("""
                - **2023-10-01** 系统维护通知
                - **2023-09-25** 新增数据分析功能
                - **2023-09-15** 用户界面优化
                """)

            with tab2:
                st.markdown("""
                - **项目A** 进度已达75%
                - **项目B** 已完成需求评审
                - **项目C** 进入测试阶段
                """)

            with tab3:
                st.markdown("""
                - 如何创建新项目
                - 数据导入指南
                - 常见问题解答
                """)
            with tab4:
                st.markdown("""
                - 如何创建新项目
                - 数据导入指南
                - 常见问题解答
                """)
