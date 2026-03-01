import streamlit as st
from utils.auth import logout_user
from utils.ats_engine import analyze_resume
import time

def process_analysis(pdf_file, job_url):
    # This acts as a loading state while we run the backend models
    with st.spinner("Analyzing semantics and checking ATS compatibility... This might take a few seconds on first run to load Models."):
        # Pass the bytes of the uploaded PDF 
        pdf_bytes = pdf_file.getvalue()
        
        # Call the real NLP engine
        result = analyze_resume(pdf_bytes, job_url)
        
        if "error" not in result and result.get("score", 0) > 0:
            from utils.history import save_analysis_history
            save_analysis_history(st.session_state.user_id, job_url, result.get("job_title", "Unknown Job"), result.get("score", 0))
            
        st.session_state.analysis_result = result
        st.session_state.current_view = 'results'
        st.rerun()

def render():
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;'>
            <h2 class='title-gradient' style='margin: 0;'>📝 ATS Dashboard</h2>
            <div style='color: #6b7280;'>Welcome, <b>{st.session_state.username}</b></div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<div class='stCard'>", unsafe_allow_html=True)
        st.subheader("1. Upload Resume")
        pdf_file = st.file_uploader("Upload your resume in PDF format", type=["pdf"])
        
        st.subheader("2. Target Job Description")
        job_url = st.text_input("Paste the URL of the job posting (LinkedIn, Indeed, Company Site)")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 Analyze ATS Compatibility", use_container_width=True):
            if not pdf_file:
                st.error("Please upload a resume (PDF).")
            elif not job_url:
                st.error("Please provide a job URL.")
            else:
                st.session_state.pdf_file = pdf_file
                st.session_state.job_url = job_url
                process_analysis(pdf_file, job_url)
                
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='stCard'>", unsafe_allow_html=True)
        st.subheader("History")
        
        from utils.history import get_user_history
        history = get_user_history(st.session_state.user_id)
        
        if not history:
            st.info("No past analyses found. Run your first analysis to see history here.")
        else:
            for item in history:
                color = "#10b981" if item["ats_score"] >= 80 else "#f59e0b" if item["ats_score"] >= 50 else "#ef4444"
                title = item["job_title"] if item["job_title"] else "Unknown Job"
                if len(title) > 35: title = title[:35] + "..."
                st.markdown(f'''
                <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <div style="font-weight: 600; font-size: 0.9rem; color: #f3f4f6; margin-bottom: 4px;" title="{item['job_title']}">{title}</div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.8rem; color: #9ca3af; text-decoration: none;">
                            <a href="{item['job_url']}" target="_blank" style="color: #60a5fa;">Link</a> • {str(item["created_at"])[:10]}
                        </span>
                        <span style="font-weight: 800; color: {color};">{item["ats_score"]}%</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("Logout", key="logout_btn"):
            logout_user()
            st.rerun()
