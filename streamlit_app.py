import streamlit as st

def main():
    st.title("我的Streamlit应用")
    st.write("这是一个使用Streamlit作为前端的应用程序！")
    
    # 添加一些交互元素
    if st.button("点击我"):
        st.snow()
        st.success("按钮被点击了！")
        
    name = st.text_input("输入你的名字", "")
    if name:
        st.write(f"你好, {name}!")
        
    number = st.slider("选择一个数字", 0, 100, 50)
    st.write(f"你选择的数字是: {number}")
    
    # 添加更多组件
    option = st.selectbox(
        "选择你喜欢的颜色",
        ("红色", "蓝色", "绿色", "黄色")
    )
    st.write(f"你选择了: {option}")

if __name__ == "__main__":
    main()