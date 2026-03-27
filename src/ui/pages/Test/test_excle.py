import os

import pandas as pd
import streamlit as st
import xlwings as xw

from src.ui.utils import save_uploaded_file


def get_active():
    try:
        return xw.books.active.name
    except xw.XlwingsError as e:
        match e:
            case "Couldn't find any active App!":
                st.toast(f"请选择一个工作簿 \n  {e}", icon="❌")
            case _:
                st.toast(f"哈哈未知 \n  {e}", icon="❌")


def get_range():
    try:
        return xw.books.active.api.Application.Selection.Value
    except xw.XlwingsError as e:
        st.toast(f"请选择一个工作簿 \n  {e}", icon="❌")


if __name__ == "__main__":
    if st.button("获取当前选择区域"):
        st.write(get_active())
        st.write(pd.DataFrame(get_range()))

    file = st.file_uploader("上传文件", type=["xlsx", "xls"])
    if file:
        st.help(file)
        st.write(file)

        # 添加保存路径输入
        save_path = st.text_input(
            "指定保存文件夹路径",
            value=os.path.join(
                os.getcwd(), "uploads"
            ),  # 默认保存到当前目录下的uploads文件夹
            help="请输入要保存文件的完整文件夹路径",
        )

        if st.button("保存文件"):
            if save_path.strip():
                saved_path = save_uploaded_file(file, save_path.strip())
                if saved_path:
                    st.success(f"文件已成功保存到: {saved_path}")
                else:
                    st.error("文件保存失败！")
            else:
                st.warning("请输入有效的保存路径！")
