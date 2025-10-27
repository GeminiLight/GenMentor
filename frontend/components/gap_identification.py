import streamlit as st

from utils.request_api import create_learner_profile, identify_skill_gap


def render_identifying_skill_gap(goal):
    with st.spinner('Identifying Skill Gap ...'):
        learning_goal = goal["learning_goal"]
        learner_information = st.session_state["learner_information"]
        llm_type = st.session_state["llm_type"]
        skill_gaps = identify_skill_gap(learning_goal, learner_information, llm_type)
    goal["skill_gaps"] = skill_gaps
    st.rerun()
    st.toast("🎉 Successfully identify skill gaps!")
    return skill_gaps


def render_identified_skill_gap(goal, method_name="genmentor"):
    """
    Render skill gaps in a card-style with prev/next switching.
    """
    levels = ["unlearned", "beginner", "intermediate", "advanced"]

    # Initialize index for card switching
    if "skill_gap_index" not in st.session_state:
        st.session_state["skill_gap_index"] = 0

    total = len(goal.get("skill_gaps", []))
    if total == 0:
        st.info("No skills identified yet.")
        return

    # Clamp index to valid range
    st.session_state["skill_gap_index"] = max(0, min(st.session_state["skill_gap_index"], total - 1))
    idx = st.session_state["skill_gap_index"]

    # Navigation controls
    nav_left, nav_center, nav_right = st.columns([2, 3, 2])
    with nav_left:
        if st.button("◀", use_container_width=True, disabled=(idx <= 0), key="skill_prev_btn"):
            st.session_state["skill_gap_index"] = max(0, idx - 1)
            st.rerun()
    with nav_center:
        st.markdown(
            f"<div style='text-align:center; font-weight:600;'>Skill   {idx+1} / {total}</div>",
            unsafe_allow_html=True,
        )
        st.progress((idx + 1) / total)
    with nav_right:
        if st.button("▶", use_container_width=True, disabled=(idx >= total - 1), key="skill_next_btn"):
            st.session_state["skill_gap_index"] = min(total - 1, idx + 1)
            st.rerun()

    # Current skill card
    skill_id = idx
    skill_info = goal["skill_gaps"][skill_id]
    skill_name = skill_info["name"]
    required_level = skill_info["required_level"]
    current_level = skill_info["current_level"]

    background_color = "#ffe6e6" if skill_info["is_gap"] else "#e6ffe6"
    text_color = "#ff4d4d" if skill_info["is_gap"] else "#33cc33"

    with st.container(border=True):
        # Card header
        st.markdown(
            f"""
            <div style="background-color: {background_color}; color: {text_color}; padding: 10px 16px; border-radius: 8px; margin-bottom: 12px; display: flex; align-items: center; min-height: 44px;">
                <p style="font-weight: 700; margin: 0; flex: 1;">{skill_id+1:2d}. {skill_name}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Required level selector
        new_required_level = st.pills(
            "**Required Level**",
            options=levels,
            selection_mode="single",
            default=required_level,
            disabled=False,
            key=f"required_{skill_name}_{method_name}",
        )
        if new_required_level != required_level:
            goal["skill_gaps"][skill_id]["required_level"] = new_required_level
            if levels.index(new_required_level) > levels.index(goal["skill_gaps"][skill_id]["current_level"]):
                goal["skill_gaps"][skill_id]["is_gap"] = True
            else:
                goal["skill_gaps"][skill_id]["is_gap"] = False
            st.rerun()

        # Current level selector
        new_current_level = st.pills(
            "**Current Level**",
            options=levels,
            selection_mode="single",
            default=current_level,
            disabled=False,
            key=f"current_{skill_name}__{method_name}",
        )
        if new_current_level != current_level:
            goal["skill_gaps"][skill_id]["current_level"] = new_current_level
            if levels.index(new_current_level) < levels.index(goal["skill_gaps"][skill_id]["required_level"]):
                goal["skill_gaps"][skill_id]["is_gap"] = True
            else:
                goal["skill_gaps"][skill_id]["is_gap"] = False
            st.rerun()

        # Details
        with st.expander("More Analysis Details"):
            if levels.index(goal["skill_gaps"][skill_id]["current_level"]) < levels.index(goal["skill_gaps"][skill_id]["required_level"]):
                st.warning("Current level is lower than the required level!")
                goal["skill_gaps"][skill_id]["is_gap"] = True
            else:
                st.success("Current level is equal to or higher than the required")
                goal["skill_gaps"][skill_id]["is_gap"] = False
            st.write(f"**Reason**: {skill_info['reason']}")
            st.write(f"**Confidence Level**: {skill_info['level_confidence']}")

        # Gap toggle
        old_gap_status = skill_info["is_gap"]
        gap_status = st.toggle(
            "Mark as Gap",
            value=skill_info["is_gap"],
            key=f"gap_{skill_name}_{method_name}",
            disabled=not skill_info["is_gap"],
        )
        if gap_status != old_gap_status:
            goal["skill_gaps"][skill_id]["is_gap"] = gap_status
            if not goal["skill_gaps"][skill_id]["is_gap"]:
                goal["skill_gaps"][skill_id]["current_level"] = goal["skill_gaps"][skill_id]["required_level"]
            st.rerun()

