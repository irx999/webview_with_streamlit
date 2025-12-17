import pandas as pd
import streamlit as st

from src.modules.ps_of_py.ps import Photoshop
from src.ui.utils import st_file_picker, st_folder_picker


def load_ps_settings():
    with st.expander("⚙️ 配置参数", expanded=True):
        # PSD文件配置
        c1 = st.columns(2)
        with c1[0]:
            psd_name_path = st_file_picker("PSD文件名")
            st.badge(str(psd_name_path), icon="📁")
        with c1[1]:
            export_folder = st_folder_picker("导出文件夹")
            st.badge(str(export_folder), icon="📁")

        # 导出配置
        c2 = st.columns(3)
        suffix = c2[0].text_input("文件名后缀", "", key="suffix")
        file_format = c2[1].segmented_control(
            "导出格式", ["png", "jpg", "jpeg"], key="file_format", default="png"
        )
        close_ps = c2[2].segmented_control(
            "完成后关闭", options=[True, False], key="close_ps", default=False
        )
        settings: dict = {
            "psd_name": psd_name_path.name,
            "psd_dir_path": psd_name_path.parent._str,
            "export_folder": export_folder._str,
            "file_format": file_format if file_format else "png",
            "suffix": suffix,
            "colse_ps": close_ps if close_ps else False,
        }
    return settings


def show():
    st.set_page_config(page_title="Photoshop自动化工具", layout="wide")
    st.title("📸 Photoshop自动化工具")

    # 主界面
    tab1, tab2, tab3 = st.tabs(["📊 数据加载", "🎨 Photoshop处理", "🖼️ 图片合并"])

    with tab1:
        st.header("配置设置")
        ps_settings = load_ps_settings()
        st.write(ps_settings)
        if st.button("开始处理"):
            with st.spinner("处理中..."):
                ps = Photoshop(**ps_settings)
                st.write(ps.get_psd_info())
                st.dataframe(pd.DataFrame(ps.get_psd_info()["all_layer"]))
                ps.ps_saveas("test.png")

        pass
    with tab2:
        pass

    with tab3:
        pass


if __name__ == "__main__":
    show()
