import os
import re
from pathlib import Path

import streamlit as st
from streamlit import session_state as ss


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


def st_folder_picker(name: str = "选择文件夹") -> Path:
    # Import tkinter
    import tkinter as tk
    from tkinter import filedialog

    # Set up tkinter
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", 1)

    clicked = st.button(label=name, key=name)
    if clicked:
        dir_path = filedialog.askdirectory(
            master=root,  # type: ignore
        )
        if dir_path == "":
            dir_path = ss.get(f"{name}_folder_path", os.getcwd())
        st.badge(dir_path, icon="📁")
        ss[f"{name}_folder_path"] = dir_path
        return Path(dir_path)

    return Path(os.getcwd())
