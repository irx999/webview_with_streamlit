import json

import requests
import streamlit as st

from src.ui.utils import st_markdown
from src.utils.config_manager import ConfigManager

dingrobot_config = ConfigManager("assets/config.json", "dingrobot_config")


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
    access_token = st.text_input(
        "Access Token",
        value=dingrobot_config.get("access_token"),
    )
    safe_word = st.text_input(
        "安全词",
        value=dingrobot_config.get("safe_word"),
    )

    dingrobot_config["access_token"] = access_token
    dingrobot_config["safe_word"] = safe_word


def main():
    # 创建左右两列布局
    c = st.columns(4, vertical_alignment="bottom")
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
            "选择模板", options=list(template_options.keys())
        )
        title = c[1].text_input("消息标题", value="默认标题")
        markdown_content = st.text_area(
            "编写你的 Markdown 内容",
            value=template_options[selected_template],
            height=400,
        )
        if c[2].button("DingBot配置", icon="⚙️"):
            app_setting()

    with col2:
        # 实时预览Markdown内容
        with st.container(border=True):
            if markdown_content:
                st.space("stretch")
                st_markdown(markdown_content)
            else:
                st.info("在左侧输入Markdown内容以查看预览")

        # 发送按钮
        if c[3].button("发送消息", type="primary", icon="📨"):
            if dingrobot_config["access_token"] and title and markdown_content:
                config = {
                    "access_token": dingrobot_config["access_token"],
                    "safe_word": dingrobot_config["safe_word"],
                }

                ding = Dingrobot(config)
                result = ding.send(title, markdown_content)

                if result == "ok":
                    st.success(f"✅ 消息 '{title}' 发送成功！")
                else:
                    st.error(f"❌ 发送失败: {result}")
            else:
                st.warning("⚠️ 请填写完整的信息（Access Token、标题和内容）")


if __name__ == "__main__":
    main()
