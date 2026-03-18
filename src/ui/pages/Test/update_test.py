import streamlit as st

from src.manager.plugins_manager import Plugins_Manager


def test_a():
    st.header("更新检测")

    pluginManager = Plugins_Manager()

    st.write(pluginManager)
    st.write(pluginManager.is_development_mode())
    for i in pluginManager.load_plugins().items():
        st.write(i)
    if st.button("检查更新"):
        pluginManager.check_for_updates(
            "ps_of_py", "irx999/ps_of_py", "dev_for_better_tools"
        )
    if st.button("更新"):
        pluginManager.update_plugin(
            "ps_of_py", "irx999/ps_of_py", "dev_for_better_tools"
        )


if __name__ == "__main__":
    test_a()
