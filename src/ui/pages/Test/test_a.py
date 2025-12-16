import streamlit as st


def test_a():
    st.header("hello world")

    from src.ui.utils import st_folder_picker

    dir_path = st_folder_picker()

    # 遍历目录中的文件
    for file in dir_path.iterdir():
        if file.is_file():  # 确保是文件而不是子目录
            if file.suffix in [".jpg", ".png"]:  # 确保是图片文件
                st.write(file.name)
                st.image(str(file), width=200)


if __name__ == "__main__":
    st.title("Test")
    test_a()
