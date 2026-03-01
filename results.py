import streamlit as st

def render():
    st.markdown("""
        <div style='display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem;'>
            <h2 class='title-gradient' style='margin: 0;'>📊 Analysis Results</h2>
        </div>
    """, unsafe_allow_html=True)
    
    if 'analysis_result' not in st.session_state:
        st.warning("No analysis data found.")
        if st.button("Go Back"):
            st.session_state.current_view = 'dashboard'
            st.rerun()
        return
        
    result = st.session_state.analysis_result
    score = result.get('score', 0)
    
    # Determine color class and CSS variable for the circle
    score_class = 'score-low'
    if score >= 80:
        score_class = 'score-high'
    elif score >= 50:
        score_class = 'score-med'
        
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("<div class='stCard' style='text-align: center;'>", unsafe_allow_html=True)
        st.subheader("ATS Match Score")
        st.markdown(f"""
            <div class='score-circle {score_class}' style='--score: {score}%;'>
                {score}%
            </div>
            <p style='margin-top: 1rem; color: #9ca3af;'>Accuracy based on semantic keyword matching.</p>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.expander("📄 View Parsed Job Description"):
            st.text(result.get('jd_text', 'No JD text extracted.'))
            

        
        if st.button("← Analyze Another Resume", use_container_width=True):
            st.session_state.current_view = 'dashboard'
            del st.session_state.analysis_result
            st.rerun()
            
    with col2:
        st.markdown("<div class='stCard'>", unsafe_allow_html=True)
        st.subheader("💡 Improvement Suggestions")
        
        if result.get('suggestions'):
            for sug in result['suggestions']:
                st.markdown(f"<div class='suggestion-item'>{sug}</div>", unsafe_allow_html=True)
        else:
            st.success("Your resume looks great! No major improvements suggested.")
            
        st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)
        
        st.subheader("🔑 Missing Keywords (Semantically)")
        if result.get('missing_skills'):
            cols = st.columns(3)
            for i, skill in enumerate(result['missing_skills']):
                cols[i % 3].error(skill)
        else:
            st.success("You matched all key requirements!")
            
        st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)
            
        st.subheader("✅ Matched Keywords")
        if result.get('resume_skills'):
            cols = st.columns(3)
            for i, skill in enumerate(result['resume_skills']):
                cols[i % 3].success(skill)
                
        st.markdown("</div>", unsafe_allow_html=True)
