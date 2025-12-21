import streamlit as st

from src.modules.ps_of_py.ps import Image_utils, LoadData, Photoshop
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
        # st.write(ps_settings)
        # if st.button("获取psd信息"):
        #     with st.spinner("处理中..."):
        #         ps = Photoshop(**ps_settings)
        #         # st.write(ps.get_psd_info())

        if st.button("一键启动"):
            with st.spinner("处理中..."):
                ps = Photoshop(**ps_settings)
                load_data = LoadData()
                with ps:
                    # for merge_name in load_data.merge_names:

                    merge_dict = {}
                    for task in load_data.selected_skus():
                        merge_list = task["任务名"].split("|")
                        if len(merge_list) > 1:
                            if merge_list[0] not in merge_dict:
                                merge_dict[merge_list[0]] = []
                            merge_dict[merge_list[0]].append(
                                merge_list[1] + ps.suffix + "." + ps.file_format
                            )

                        ps.core(task["任务名"], task["修改信息"])

                    # ps.app.doJavaScript(f'alert("save to jpg: {ps.export_folder}")')
                print(merge_dict)

                for merge_name, merge_list in merge_dict.items():
                    Image_utils.merge_images(
                        ps.export_folder + "/" + merge_name,
                        merge_list,
                        merge_name + "(1)." + ps_settings["file_format"],
                    )

    with tab2:
        pass

    with tab3:
        pass


if __name__ == "__main__":
    show()
