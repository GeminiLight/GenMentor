import streamlit as st
import time
from utils.state import initialize_session_state, change_selected_goal_id, save_persistent_state, load_persistent_state
initialize_session_state()


st.session_state.setdefault("_autosave_enabled", True)
try:
    save_persistent_state()
except Exception:
    pass

from components.chatbot import render_chatbot

st.set_page_config(page_title="GenMentor", page_icon="🧠", layout="wide")
st.logo("./assets/avatar.png")
st.markdown('<style>' + open('./assets/css/main.css').read() + '</style>', unsafe_allow_html=True)

if st.session_state["show_chatbot"]:
    render_chatbot()

if st.session_state["if_complete_onboarding"]:
    onboarding = st.Page("pages/onboarding.py", title="Onboarding", icon=":material/how_to_reg:", default=False)
    learning_path = st.Page("pages/learning_path.py", title="Learning Path", icon=":material/route:", default=True)
else:
    onboarding = st.Page("pages/onboarding.py", title="Onboarding", icon=":material/how_to_reg:", default=True)
    learning_path = st.Page("pages/learning_path.py", title="Learning Path", icon=":material/route:", default=False)
skill_gaps = st.Page("pages/skill_gap.py", title="Skill Gap", icon=":material/insights:", default=False)
knowledge_document = st.Page("pages/knowledge_document.py", title="Resume Learning", icon=":material/menu_book:", default=False)
learner_profile = st.Page("pages/learner_profile.py", title="My Profile", icon=":material/person:", default=False)
goal_management = st.Page("pages/goal_management.py", title="Goal Management", icon=":material/flag:", default=False)
dashboard = st.Page("pages/dashboard.py", title="Analytics Dashboard", icon=":material/browse:", default=False)

# Learning Analytics Dashboard
if not st.session_state["if_complete_onboarding"]:
    nav_position = "sidebar"
    pg = st.navigation({"GenMentor": [onboarding, skill_gaps, learning_path]}, position="hidden", expanded=True)
else:
    nav_position = "sidebar"
    pg = st.navigation({"GenMentor": [goal_management, learning_path, knowledge_document, learner_profile, dashboard]}, position=nav_position, expanded=True)
    goal = st.session_state["goals"][st.session_state["selected_goal_id"]]
    goal['start_time'] = time.time()
    try:
        save_persistent_state()
    except Exception:
        pass
    unlearned_skill = len(goal['learner_profile']['cognitive_status']['in_progress_skills'])
    learned_skill = len(goal['learner_profile']['cognitive_status']['mastered_skills'])
    all_skill = learned_skill + unlearned_skill

    if goal['id'] not in st.session_state['learned_skills_history']:
        st.session_state['learned_skills_history'][goal['id']] = []
        try:
            save_persistent_state()
        except Exception:
            pass

    if all_skill != 0:
        # mastery_rate = math.floor(mastery_rate * 100)
        mastery_rate = learned_skill / all_skill if all_skill != 0 else 0
        if st.session_state['learned_skills_history'][goal['id']] == []:
            st.session_state['learned_skills_history'][goal['id']].append(mastery_rate)
            try:
                save_persistent_state()
            except Exception:
                pass
    if(time.time()-goal['start_time']>600):
        goal['start_time'] = time.time()
        try:
            save_persistent_state()
        except Exception:
            pass
        st.session_state['learned_skills_history'][goal['id']].append(mastery_rate)
        try:
            save_persistent_state()
        except Exception:
            pass

    if len(st.session_state['learned_skills_history'][goal['id']]) > 10:
        st.session_state['learned_skills_history'][goal['id']].pop(0)
        try:
            save_persistent_state()
        except Exception:
            pass

    # persist updates to learned skills history and goal state
    try:
        save_persistent_state()
    except Exception:
        pass

# Automatic save on every script run if enabled
try:
    if st.session_state.get("_autosave_enabled", True):
        save_persistent_state()
except Exception:
    pass

if len(st.session_state["goals"]) != 0:
    change_selected_goal_id(st.session_state["selected_goal_id"])
    try:
        save_persistent_state()
    except Exception:
        pass

pg.run()


# st.sidebar.button("Toggle Chatbot", on_click=lambda: st.session_state["show_chatbot"] == False)