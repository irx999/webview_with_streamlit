import streamlit as st


def main():
    with st.container(
        width=400,
        height=400,
        horizontal=True,
        vertical_alignment="center",
        horizontal_alignment="center",
        border=True,
    ):
        st.space("stretch")
        st.button("点击")
        st.space("stretch")
        st.button("点击2")
        st.space("stretch")

    c = st.columns(5, vertical_alignment="bottom", border=True, width="stretch")

    st.space("stretch")
    c[1].button("点击1231", use_container_width=True)
    st.space("stretch")
    c[3].button("点击1232")
    st.space("stretch")

    form = st.form("my_form")
    form.slider("Inside the form")
    st.slider("Outside the form")

    # Now add a submit button to the form:
    form.form_submit_button("Submit")


if __name__ == "__main__":
    main()
