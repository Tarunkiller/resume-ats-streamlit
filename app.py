import streamlit as st
from utils.auth import init_auth, is_authenticated
from views import login, dashboard, results

st.set_page_config(
    page_title="High-Accuracy ATS Resume Maker",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Custom CSS
def load_css():
    try:
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

def main():
    load_css()
    init_auth()

    if not is_authenticated():
        login.render()
    else:
        # Simple navigation
        if st.session_state.get('current_view', 'dashboard') == 'dashboard':
            dashboard.render()
        elif st.session_state.get('current_view') == 'results':
            results.render()

if __name__ == "__main__":
    main()
