from typing import Any

import streamlit as st

from ..utils import get_path

HP = get_path("src/ui/pages/")

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
            HP + "Test/test_excle.py",
            title="excel 测试页",
            icon="🧪",
        ),
        st.Page(
            HP + "Test/update_test.py",
            title="update_test",
            icon="🧪",
        ),
    ],
}
try:
    from plugins.ps_of_py.src.ui import pages

    PAGES |= pages

except ImportError as e:
    print(f"未找到插件{e}")
