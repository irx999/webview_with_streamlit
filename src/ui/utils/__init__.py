import re

import streamlit as st


def st_markdown(markdown_string):
    parts = re.split(r"!\[(.*?)\]\((.*?)\)", markdown_string)
    for i, part in enumerate(parts):
        if i % 3 == 0:
            st.markdown(
                part,
                unsafe_allow_html=True,
            )
        elif i % 3 == 1:
            # title = part
            pass
        else:
            st.image(part, width="content")
