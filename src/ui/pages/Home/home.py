import streamlit as st

if __name__ == "__main__":
    col1, col2 = st.columns([1, 1], border=False, vertical_alignment="center")

    with col1:
        # 右侧区域 - 您所说的"左下角"容器（实际是页面右侧）
        # st.container(height=250, border=False)
        with st.container(
            border=False, vertical_alignment="center", horizontal_alignment="center"
        ):
            carousel_container = st.container()
            with carousel_container:
                st.image("assets/images/Banner3-large-cn.png")
            # 三个公告tabs
            tab1, tab2, tab3, tab4 = st.tabs(
                ["系统公告", "项目动态", "使用指南", "哈哈"]
            )

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
    with col2:
        pass
