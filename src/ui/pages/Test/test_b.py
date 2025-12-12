import pandas as pd
import streamlit as st

from src.test.test import get_active, get_range

if __name__ == "__main__":
    if st.button("获取当前选择区域"):
        st.write(get_active())

        st.write(pd.DataFrame(get_range()))

    st.file_uploader("上传文件", type=["xlsx", "xls"])
