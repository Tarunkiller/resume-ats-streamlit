import streamlit as st
import bcrypt
from database import get_connection

def init_auth():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'dashboard'

def is_authenticated():
    return st.session_state.get('authenticated', False)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password(password, user['password_hash']):
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.user_id = user['id']
        st.session_state.current_view = 'dashboard'
        return True
    return False

def register_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Username already exists"
        
    try:
        hashed = hash_password(password)
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed))
        conn.commit()
        conn.close()
        return True, "Registration successful. Please login."
    except Exception as e:
        conn.close()
        return False, str(e)

def logout_user():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.current_view = 'login'
