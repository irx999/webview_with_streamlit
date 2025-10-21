import random

import streamlit as st


def test_a():
    for i in range(9):
        # with st.container(border=True, height=100, key=i):
        #     pass
        num = random.randint(1, 100)
        c = st.columns(2)
        c[0].image(f"https://quickchart.io/qr?text={num}", width=80)
        c[1].write(f"This is a {num}")


if __name__ == "__main__":
    st.title("Test")
    test_a()
