import pandas as pd
import streamlit as st
import xlwings as xw


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

    st.file_uploader("上传文件", type=["xlsx", "xls"])
