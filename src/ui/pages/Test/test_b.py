import streamlit as st

from src.utils.config_manager import ConfigManager

app_config2 = ConfigManager("assets/config.toml", "app_config2")


def test_a():
    st.header("hello world")


if __name__ == "__main__":
    st.title("Test")
    test_a()
