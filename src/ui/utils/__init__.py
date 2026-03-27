import os
import re
import sys
from pathlib import Path

import streamlit as st
from streamlit import session_state as ss


def st_markdown(markdown_string):
    """
    Markdown 显示

    支持解析和渲染包含图片链接的 Markdown 文本，将文本部分用 st.markdown 渲染，
    图片部分用 st.image 渲染，实现富文本显示效果

    Args:
        markdown_string (str): 包含图片链接的 Markdown 字符串

    Returns:
        None: 直接在 Streamlit 界面中渲染内容
    """

    parts = re.split(r"!\[(.*?)\]\((.*?)\)", markdown_string)
    for i, part in enumerate(parts):
        if i % 3 == 0:
            # 渲染纯文本部分
            st.markdown(
                part,
                unsafe_allow_html=True,
            )
        elif i % 3 == 1:
            # 这部分是图片的 alt 文本（跳过）
            pass
        else:
            # 渲染图片部分
            st.image(part, width="content")


def st_file_picker(
    name: str = "选择文件", button_icon=None, filetypes=None, default: str = os.getcwd()
) -> Path:
    """
    文件选择器组件

    创建一个按钮，点击后打开文件选择对话框，允许用户选择文件。
    选择的文件路径会保存到 session state 中，方便后续使用。

    Args:
        name (str): 按钮显示的名称，默认为"选择文件"
        button_icon: 按钮图标，默认无图标
        filetypes: 文件类型过滤器，接受元组列表格式 [("扩展名", "描述"), ...]
        default (str): 默认路径，当没有选择文件时返回此路径，默认为当前工作目录

    Returns:
        Path: 用户选择的文件路径，如果未选择则返回默认路径
    """

    import tkinter as tk
    from tkinter import filedialog

    # 设置 tkinter 根窗口（隐藏）
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", 1)

    clicked = st.button(label=name, key=name, icon=button_icon if button_icon else None)

    if clicked:
        dir_path = filedialog.askopenfilename(
            master=root,  # type: ignore
            initialdir=os.getcwd(),
            filetypes=filetypes if filetypes else [("All Files", "*.*")],
            initialfile=default,
        )

        # 如果用户取消选择，则返回当前保存的路径或默认路径
        if dir_path == "":
            return Path(ss.get(f"{name}_file_path", os.getcwd()))

        # 保存选择的路径到 session state
        # ss[f"{name}_file_path"] = dir_path
        return Path(dir_path)

    return Path(default)


def st_folder_picker(
    name: str = "选择文件夹", button_icon=None, default: str = os.getcwd()
) -> Path:
    """
    文件夹选择器组件

    创建一个按钮，点击后打开文件夹选择对话框，允许用户选择文件夹。
    选择的文件夹路径会保存到 session state 中，方便后续使用。

    Args:
        name (str): 按钮显示的名称，默认为"选择文件夹"
        button_icon: 按钮图标，默认无图标
        default (str): 默认路径，当没有选择文件夹时返回此路径，默认为当前工作目录

    Returns:
        Path: 用户选择的文件夹路径，如果未选择则返回默认路径
    """

    import tkinter as tk
    from tkinter import filedialog

    # 设置 tkinter 根窗口（隐藏）
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", 1)

    clicked = st.button(label=name, key=name, icon=button_icon if button_icon else None)

    if clicked:
        dir_path = filedialog.askdirectory(
            master=root,  # type: ignore
            initialdir=default,
        )

        # 如果用户取消选择，则返回当前保存的路径或默认路径
        if dir_path == "":
            return Path(ss.get(f"{name}_folder_path", os.getcwd()))

        # 保存选择的路径到 session state
        # ss[f"{name}_folder_path"] = dir_path
        return Path(dir_path)

    return Path(default)


def get_path(path) -> str:
    """
    获取文件路径

    根据不同场景返回真实文件路径
    主要用于支持PyInstaller打包后的可执行文件获取资源文件路径

    Args:
        path (str): 相对于执行文件的相对路径

    Returns:
        str: 实际的文件路径
            - 如果是在PyInstaller打包环境下运行，返回_MEIPASS中的路径
            - 否则返回当前工作目录下的路径

    Example:
        >>> config_path = get_path("config/settings.json")
        >>> print(config_path)
        "/path/to/resource/config/settings.json"
    """

    if hasattr(sys, "_MEIPASS"):
        # PyInstaller 打包后，_MEIPASS 属性指向临时资源目录
        return os.path.join(sys._MEIPASS, path)  # type: ignore
    else:
        # 普通 Python 脚本运行环境，返回当前工作目录下的路径
        return os.path.join(os.getcwd(), path)


def get_path2(__file__, file_name) -> str:
    """
    获取文件路径

    根据不同场景返回真实文件路径
    主要用于获取与当前文件相关的资源文件路径

    Args:
        __file__ (str): 当前模块的文件路径（通常传入__file__变量）
        file_name (str): 要获取的文件名或相对路径

    Returns:
        str: 与当前文件同目录下的实际文件路径

    Example:
        >>> # 在某个.py文件中
        >>> template_path = get_path2(__file__, "template.html")
        >>> print(template_path)
        "/path/to/current/directory/template.html"
    """

    # 获取当前文件所在目录，并与目标文件名拼接
    return os.path.join(os.path.dirname(__file__), file_name)


def save_uploaded_file(uploaded_file, save_directory):
    """保存上传的文件到指定目录

    Args:
        uploaded_file: Streamlit 上传的文件对象，需具有 name 属性和 getbuffer() 方法
        save_directory (str): 文件保存的目标目录路径

    Returns:
        Optional[str]: 成功时返回保存的完整文件路径，失败时返回 None
    """
    try:
        # 确保保存目录存在
        os.makedirs(save_directory, exist_ok=True)

        # 构建完整的文件路径
        file_path = os.path.join(save_directory, uploaded_file.name)

        # 保存文件
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return file_path
    except Exception as e:
        st.error(f"保存文件时出错: {str(e)}")
        return None
