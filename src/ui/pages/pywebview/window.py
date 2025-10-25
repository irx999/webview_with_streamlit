import requests
import streamlit as st
from streamlit import session_state as ss


def get_window_size():
    try:
        width_response = requests.get(
            "http://127.0.0.1:48000/api/v1/pywebview/window/get?property=width",
            timeout=5
        )
        # 检查响应是否为空或非JSON格式
        if not width_response.text.strip():
            print("警告: 窗口宽度API返回空响应")
            return 1200, 800
            
        width_data = width_response.json()
        width = width_data["data"]
        
        height_response = requests.get(
            "http://127.0.0.1:48000/api/v1/pywebview/window/get?property=height",
            timeout=5
        )
        # 检查响应是否为空或非JSON格式
        if not height_response.text.strip():
            print("警告: 窗口高度API返回空响应")
            return 1200, 800
            
        height_data = height_response.json()
        height = height_data["data"]

        return int(width), int(height)
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        # 返回默认尺寸
        return 1200, 800
    except ValueError as e:
        print(f"JSON解析错误: {e}")
        print(f"收到的响应内容: {width_response.text if 'width_response' in locals() else 'N/A'}")
        return 1200, 800
    except Exception as e:
        print(f"获取窗口尺寸时发生未知错误: {e}")
        return 1200, 800


def set_window_size() -> None:
    try:
        width = ss.get("width", 1200)
        height = ss.get("height", 800)
        response = requests.post(
            "http://127.0.0.1:48000/api/v1/pywebview/window/set",
            json={"func": "resize", "width": width, "height": height},
            timeout=5
        )
        # 检查响应是否为空
        if not response.text.strip():
            print("警告: 窗口调整API返回空响应")
            return
            
        result = response.json()
        if result.get("status") != "success":
            print(f"窗口调整失败: {result.get('data', '未知错误')}")
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
    except ValueError as e:
        print(f"JSON解析错误: {e}")
        print(f"收到的响应内容: {response.text if 'response' in locals() else 'N/A'}")
    except Exception as e:
        print(f"设置窗口尺寸时发生未知错误: {e}")


def change_window_fullscreen() -> None:
    try:
        response = requests.post(
            "http://127.0.0.1:48000/api/v1/pywebview/window/set",
            json={"func": "toggle_fullscreen"},
            timeout=5
        )
        # 检查响应是否为空
        if not response.text.strip():
            print("警告: 全屏切换API返回空响应")
            return
            
        result = response.json()
        if result.get("status") != "success":
            print(f"全屏切换失败: {result.get('data', '未知错误')}")
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
    except ValueError as e:
        print(f"JSON解析错误: {e}")
        print(f"收到的响应内容: {response.text if 'response' in locals() else 'N/A'}")
    except Exception as e:
        print(f"切换全屏时发生未知错误: {e}")


def change_on_top() -> None:
    try:
        import time
        time.sleep(0.1)
        response = requests.post(
            "http://127.0.0.1:48000/api/v1/pywebview/window/set",
            json={"func": "on_top"},
            timeout=5
        )
        # 检查响应是否为空
        if not response.text.strip():
            print("警告: 窗口置顶API返回空响应")
            return
            
        result = response.json()
        if result.get("status") != "success":
            print(f"窗口置顶失败: {result.get('data', '未知错误')}")
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
    except ValueError as e:
        print(f"JSON解析错误: {e}")
        print(f"收到的响应内容: {response.text if 'response' in locals() else 'N/A'}")
    except Exception as e:
        print(f"切换窗口置顶时发生未知错误: {e}")


if __name__ == "__main__":
    width = st.slider(
        "输入宽度",
        1200,
        2560,
        key="width",
        step=100,
        value=get_window_size()[0],
        on_change=set_window_size,
    )
    height = st.slider(
        "输入高度",
        800,
        1440,
        key="height",
        step=100,
        value=get_window_size()[1],
        on_change=set_window_size,
    )
    st.toggle(
        "切换全屏",
        on_change=change_window_fullscreen,
    )
    st.toggle(
        "切换置顶",
        on_change=change_on_top,
    )