import streamlit as st
from config import llm_label_map


@st.dialog("Login")
def login():
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Submit", disabled=True):
        st.session_state["logged_in"]  = True
        st.rerun()
    # currently not available
    st.warning("Unavailable in this demo version.")

def logout():
    st.session_state["logged_in"] = False


def render_topbar():
    col1, col2, col3 = st.columns([2, 6, 1])
    # llm_type_list = ["GPT-4o", "Llama3.2"]
    llm_type_list = list(llm_label_map.keys())
    llm_label_list = list(llm_label_map.values())
    with col1:
        # st.button("GenMentor")
        llm_label = st.selectbox(
            "LLM Type",
            llm_label_list,
            index=llm_type_list.index(st.session_state["llm_type"]),
            label_visibility="collapsed",
        )
        st.session_state["llm_type"] = llm_type_list[llm_label_list.index(llm_label)]

    with col3:
        if st.session_state["logged_in"]:
            with st.popover("", icon=":material/account_circle:", use_container_width=True):
                logout_button = st.button("Log-out", icon=":material/exit_to_app:")
                if logout_button:
                    logout()
                    st.rerun()
        else:
            if st.button("", icon=":material/account_circle:", use_container_width=True):
                login()
