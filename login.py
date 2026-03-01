import streamlit as st
from utils.auth import login_user, register_user

def render():
    st.markdown("<h1 style='text-align: center; color: #1E3A8A; margin-bottom: 2rem;'>🎯 ATS Resume Maker Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #4B5563; margin-bottom: 3rem;'>Unlock the power of NLP to perfect your resume.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔒 Login", "📝 Register"])
        
        with tab1:
            with st.form("login_form"):
                st.subheader("Login to your account")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login", use_container_width=True)
                
                if submit:
                    if login_user(username, password):
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                        
        with tab2:
            with st.form("register_form"):
                st.subheader("Create a new account")
                new_username = st.text_input("Choose Username")
                new_password = st.text_input("Choose Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                reg_submit = st.form_submit_button("Register", use_container_width=True)
                
                if reg_submit:
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        success, message = register_user(new_username, new_password)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
