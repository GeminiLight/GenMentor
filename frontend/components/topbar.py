import streamlit as st
from config import llm_label_map
import config
from utils.state import save_persistent_state
import requests
import re
from pathlib import Path
from utils.request_api import get_available_models


@st.dialog("Login")
def login():
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Submit", disabled=True):
        st.session_state["logged_in"]  = True
        try:
            save_persistent_state()
        except Exception:
            pass
        st.rerun()
    # currently not available
    st.warning("Unavailable in this demo version.")

def logout():
    st.session_state["logged_in"] = False
    try:
        save_persistent_state()
    except Exception:
        pass


def render_topbar():
    col1, col2, col3, col4 = st.columns([1, 2, 6, 1])
    # first-time backend availability check
    if "checked_backend" not in st.session_state:
        st.session_state["checked_backend"] = False
    if not st.session_state["checked_backend"]:
        try:
            # try a fast GET to backend root
            resp = requests.get(config.backend_endpoint, timeout=1)
            models = get_available_models(config.backend_endpoint)
            st.success(f"Backend reachable. Available models: {', '.join(models)}")
            backend_ok = resp.status_code < 500
        except Exception:
            backend_ok = False
        if not backend_ok:
            st.warning("Backend not reachable. Please check your settings.")
            # open settings dialog so user can update `frontend/config.py`
            settings()
        st.session_state["checked_backend"] = True
    # llm_type_list = ["GPT-4o", "Llama3.2"]
    llm_type_list = list(llm_label_map.keys())
    llm_label_list = list(llm_label_map.values())
    # settings button on the topbar (center/right)
    with col1:
        if st.button("", icon=":material/settings:", use_container_width=False):
            settings()

    with col2:
        # st.button("GenMentor")
        llm_label = st.selectbox(
            "LLM Type",
            llm_label_list,
            index=llm_type_list.index(st.session_state["llm_type"]),
            label_visibility="collapsed",
        )
        st.session_state["llm_type"] = llm_type_list[llm_label_list.index(llm_label)]
        try:
            save_persistent_state()
        except Exception:
            pass



    with col4:
        if st.session_state["logged_in"]:
            with st.popover("", icon=":material/account_circle:", use_container_width=True):
                logout_button = st.button("Log-out", icon=":material/exit_to_app:")
                if logout_button:
                    logout()
                    st.rerun()
        else:
            if st.button("", icon=":material/account_circle:", use_container_width=True):
                login()


@st.dialog("Settings")
def settings():
    """Settings dialog to edit backend endpoint and LLM API key stored in frontend/config.py

    This writes updates back to the `frontend/config.py` file and triggers a rerun.
    """
    # current backend endpoint
    cur_backend = getattr(config, "backend_endpoint", "http://127.0.0.1:5006/")
    new_backend = st.text_input("Backend endpoint (include protocol and port)", value=cur_backend)

    # prepare inputs for each LLM type listed in config.llm_type_list or llm_label_map
    # llm_types = list(getattr(config, "llm_type_list", list(llm_label_map.keys())))
    st.markdown("---")

    # mapping from internal llm type to backend .env variable name
    # env_map = {
    #     "deepseek": "DEEPSEEK_API_KEY",
    #     "together": "TOGETHER_API_KEY",
    #     "gpt4o": "OPENAI_API_KEY",
    #     "anthropic": "ANTHROPIC_API_KEY",
    #     # llama or local models may not need a key; we'll still offer a custom var name
    #     "llama": "LLAMA_API_KEY",
    # }

    # read current backend .env values to prefill
    env_path = Path(__file__).resolve().parents[1].parent / "backend" / ".env"
    env_text = ""
    if env_path.exists():
        env_text = env_path.read_text(encoding="utf-8")

    # collect user inputs
    # inputs = {}
    # for t in llm_types:
    #     env_var = env_map.get(t, f"CUSTOM_{t.upper()}_API_KEY")
    #     # try to find existing value
    #     m = re.search(rf'^{re.escape(env_var)}=(.*)$', env_text, flags=re.M)
    #     existing = m.group(1) if m else ""
    #     # hide value as password field
    #     val = st.text_input(f"{t} ({env_var})", value=existing, type="password")
    #     inputs[env_var] = val

    col1, col2, col3  = st.columns([1, 2, 1])
    with col1:
        if st.button("Check"):
            try:
                models = get_available_models(new_backend)
                # st.session_state["checked_backend"] = True
                # st.session_state["available_models"] = models
            except Exception as e:
                st.error(f"Failed to reach backend: {e}")

    with col3:
        if st.button("Save"):
            # normalize backend
            if not new_backend.endswith("/"):
                new_backend = new_backend + "/"
            try:
                # update frontend config backend endpoint
                update_config_file(new_backend)
                # update backend .env with provided keys
                # update_backend_env(inputs)
                try:
                    save_persistent_state()
                except Exception:
                    pass
                st.success("Settings saved. Restarting app...")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to save settings: {e}")


def update_config_file(new_backend: str):
    """Update the frontend/config.py file with new backend endpoint.

    This function performs simple text replacement; it will add the variable if missing.
    """
    # config.py is in the frontend/ folder
    cfg_path = Path(__file__).resolve().parents[1] / "config.py"
    text = cfg_path.read_text(encoding="utf-8")

    # replace backend_endpoint line or append
    if re.search(r'^\s*backend_endpoint\s*=.*$', text, flags=re.M):
        text = re.sub(r'^\s*backend_endpoint\s*=.*$', f'backend_endpoint = "{new_backend}"', text, flags=re.M)
    else:
        text += f"\nbackend_endpoint = \"{new_backend}\"\n"

    # write back
    cfg_path.write_text(text, encoding="utf-8")


def update_backend_env(env_updates: dict):
    """Update or add environment variables in backend/.env file.

    env_updates: dict mapping ENV_VAR -> value
    If value is empty string, the variable will be left as-is (no deletion).
    """
    backend_env_path = Path(__file__).resolve().parents[1].parent / "backend" / ".env"
    if not backend_env_path.exists():
        # create a new .env with entries
        lines = []
    else:
        lines = backend_env_path.read_text(encoding="utf-8").splitlines()

    # convert to dict preserving comments and unknown lines
    out_lines = []
    handled = set()
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            out_lines.append(line)
            continue
        if "=" not in line:
            out_lines.append(line)
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        if k in env_updates and env_updates[k] != "":
            out_lines.append(f"{k}={env_updates[k]}")
            handled.add(k)
        else:
            out_lines.append(line)

    # append any new keys not present
    for k, v in env_updates.items():
        if k in handled or v == "":
            continue
        out_lines.append(f"{k}={v}")

    backend_env_path.write_text("\n".join(out_lines) + ("\n" if out_lines and not out_lines[-1].endswith("\n") else ""), encoding="utf-8")
