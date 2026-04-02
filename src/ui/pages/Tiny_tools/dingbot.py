import json

import requests
import streamlit as st

from src.ui.utils import st_markdown
from src.utils.config_manager import ConfigManager

dingrobot_config = ConfigManager("config.json", "dingrobot_config")


class Dingrobot:
    def __init__(self, config):
        self.access_token = config["access_token"]
        self.safe_word = config["safe_word"]

    def send(self, titel, msg: str):
        try:
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": self.safe_word + titel,
                    "text": msg,
                },
            }

            rebot_url = (
                f"https://oapi.dingtalk.com/robot/send?access_token={self.access_token}"
            )
            ans = requests.post(
                url=rebot_url,
                data=json.dumps(data),
                headers={"Content-Type": "application/json"},
                timeout=5,
            )
            assert ans.status_code == 200, ans.json()["errmsg"]
            return ans.json()["errmsg"]
        except Exception as ans:
            return ans


@st.dialog("Dingbot_Setting", width="small", icon="⚙️")
def app_setting():
    # 获取当前的机器人配置
    robots = dingrobot_config.get("robots", {})

    # 显示所有机器人的配置表单
    st.subheader("机器人配置")

    # 添加新的机器人
    with st.expander("添加新机器人"):
        new_robot_name = st.text_input("机器人名称")
        new_access_token = st.text_input("Access Token")
        new_safe_word = st.text_input("安全词")

        if st.button("添加机器人"):
            if new_robot_name and new_access_token:
                robots[new_robot_name] = {
                    "access_token": new_access_token,
                    "safe_word": new_safe_word or "",
                }
                dingrobot_config["robots"] = robots
                st.rerun()
            else:
                st.warning("请输入机器人名称和Access Token")

    # 编辑现有机器人
    for robot_name, config in robots.items():
        with st.expander(f"编辑 {robot_name}"):
            updated_access_token = st.text_input(
                "Access Token", value=config["access_token"], key=f"token_{robot_name}"
            )
            updated_safe_word = st.text_input(
                "安全词", value=config.get("safe_word", ""), key=f"safe_{robot_name}"
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"更新 {robot_name}", key=f"update_{robot_name}"):
                    robots[robot_name]["access_token"] = updated_access_token
                    robots[robot_name]["safe_word"] = updated_safe_word
                    dingrobot_config["robots"] = robots
                    st.rerun()
            with col2:
                if st.button(
                    f"删除 {robot_name}", key=f"delete_{robot_name}", type="secondary"
                ):
                    del robots[robot_name]
                    dingrobot_config["robots"] = robots
                    st.rerun()


def main():
    # 获取机器人列表
    robots = dingrobot_config.get("robots", {})

    # 创建左右两列布局
    c = st.columns(5, vertical_alignment="bottom")
    col1, col2 = st.columns(2, gap="large")

    with col1:
        # 提供一些常用的markdown模板
        template_options = {
            "基础模板": "",
            "标题模板": "### 标题\n\n你的内容在这里",
            "图文模板": "### 图文消息\n\n这里是文字内容\n\n![图片描述](http://irx999.fun/img/QVQ.gif)",
            "表格模板": "| 列1 | 列2 |\n| --- | --- |\n| 内容1 | 内容2 |",
        }

        selected_template = c[0].selectbox(
            "选择模板", options=list(template_options.keys()), width="stretch"
        )

        # 选择机器人
        if robots:
            selected_robot = c[2].selectbox(
                "选择机器人",
                options=list(robots.keys()),
                key="selected_robot",
                width="stretch",
            )
        else:
            st.warning("没有配置任何机器人，请先添加机器人")
            selected_robot = None

        title = c[1].text_input("消息标题", value="这是一个原装标题", width="stretch")

        markdown_content = st.text_area(
            " ",
            value=template_options[selected_template],
            height=400,
        )
        if c[3].button("Bot配置", icon="⚙️", width="stretch"):
            app_setting()

    with col2:
        st.space("small")
        # 实时预览Markdown内容
        # st.text("实时预览")
        with st.container(border=True):
            if markdown_content:
                st.space("stretch")
                st_markdown(markdown_content)
            else:
                st.info("在左侧输入Markdown内容以查看预览")

        # 发送按钮
        if c[4].button("发送消息", type="primary", icon="📨", width="stretch"):
            if selected_robot and title and markdown_content:
                config = robots[selected_robot]

                ding = Dingrobot(config)
                result = ding.send(title, markdown_content)

                if result == "ok":
                    st.success(
                        f"✅ 消息 '{title}' 已发送到 '{selected_robot}' 机器人！"
                    )
                else:
                    st.error(f"❌ 发送失败: {result}")
            else:
                st.warning("⚠️ 请填写完整的信息（选择机器人、标题和内容）")


if __name__ == "__main__":
    main()
