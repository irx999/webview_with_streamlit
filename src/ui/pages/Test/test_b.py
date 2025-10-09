import pandas as pd
import streamlit as st
import xlwings as xw

if __name__ == "__main__":
    if st.button("获取当前选择区域"):
        st.write(xw.sheets.active)

        df = pd.DataFrame(xw.sheets.active.api.Application.Selection.Value)
        st.write(df)
