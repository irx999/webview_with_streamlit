import os
import sys
from typing import Any

import streamlit as st


def get_script_path() -> str:
    script_path = "src/ui/pages/"
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, script_path)  # type: ignore
    else:
        return os.path.join(os.getcwd(), script_path)


def get_path(path) -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, path)  # type: ignore
    else:
        return os.path.join(os.getcwd(), path)


HP = get_script_path()


PAGES: dict[str, list[Any]] = {
    "🏠Home": [
        st.Page(
            HP + "Home/home.py",
            title="HOME",
            icon="🏠",
        ),
        st.Page(
            HP + "Home/readme.py",
            title="README",
            icon="🏠",
            default=True,
        ),
        st.Page(
            HP + "Home/changelog.py",
            title="CHANGELOG",
            icon="🏠",
        ),
    ],
    "⚙️Setting": [],
    "🧪功能测试": [
        st.Page(
            HP + "Test/test_a.py",
            title="测试页1",
            icon="🧪",
        ),
        st.Page(
            HP + "Test/test_b.py",
            title="测试页2",
            icon="🧪",
        ),
    ],
    "🎨PS自动化": [
        st.Page(
            get_path("plugins/ps_of_py/src/ui/main.py"),
            title="主界面",
            icon="🎨",
        ),
    ],
}
