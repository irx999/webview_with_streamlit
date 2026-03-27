import time

import streamlit as st

if __name__ == "__main__":
    st.container(height=200, border=False)
    col1 = st.container(
        border=False,
        # vertical_alignment="bottom",
        # horizontal_alignment="left",
        horizontal=True,
    )

    with col1:
        st.space("stretch")
        # 右侧区域 - 您所说的"左下角"容器（实际是页面右侧）
        # st.container(height=250, border=False)
        with st.container(
            border=False,
            vertical_alignment="bottom",
            horizontal_alignment="left",
            width=320,
        ):
            carousel_container = st.empty()
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

            while True:
                from src.app import App

                image_list = [
                    f"https://placehold.co/600x300/4CAF50/white?text={App.name}",
                    f"https://placehold.co/600x300/2196F3/white?text={App.version}",
                    f"https://placehold.co/600x300/FF9800/white?text={App.mtime}",
                ]
                for i, image_url in enumerate(image_list):
                    # 显示图片
                    carousel_container.image(
                        image_url, link="https://github.com/irx999"
                    )
                    time.sleep(2)
