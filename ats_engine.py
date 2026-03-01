import spacy
from sentence_transformers import SentenceTransformer, util
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
import re
import streamlit as st

# Caching models so they don't reload on every UI interaction
@st.cache_resource
def load_models():
    try:
        # Check if downloaded, if not user will need to run python -m spacy download en_core_web_sm
        _nlp = spacy.load("en_core_web_sm")
    except OSError:
        import subprocess
        import sys
        # Auto-download if missing
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        _nlp = spacy.load("en_core_web_sm")
        
    _sbert = SentenceTransformer('all-MiniLM-L6-v2')
    return _nlp, _sbert

def extract_text_from_pdf(pdf_bytes):
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        return text
    except Exception as e:
        return ""

def extract_text_from_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else url
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.extract()
            
        text = soup.get_text(separator=' ', strip=True)
        return re.sub(r'\s+', ' ', text), title.strip()
    except Exception as e:
        return "", str(url)

def extract_keywords(text, nlp_model):
    """Extracts noun phrases and key entities to act as skills/requirements."""
    doc = nlp_model(text)
    keywords = set()
    
    # Extract noun chunks (e.g., "Machine Learning", "Frontend Development")
    for chunk in doc.noun_chunks:
        phrase = chunk.text.strip().lower()
        # Filter out overly long phrases or single stop words
        if 2 <= len(phrase.split()) <= 4:
            keywords.add(phrase)
            
    # Extract single proper nouns (e.g., "React", "Python")
    for token in doc:
        if token.pos_ == "PROPN" and len(token.text) > 1:
            keywords.add(token.text.lower())
            
    return list(keywords)

def semantic_match(jd_keywords, resume_keywords, sbert_model, threshold=0.65):
    """Uses Sentence-Transformers to find semantically similar keywords instead of exact matches."""
    if not jd_keywords or not resume_keywords:
        return [], jd_keywords
        
    # Encode all keywords into embeddings
    jd_embeddings = sbert_model.encode(jd_keywords, convert_to_tensor=True)
    resume_embeddings = sbert_model.encode(resume_keywords, convert_to_tensor=True)
    
    # Compute cosine similarities between all JD and Resume keywords
    cosine_scores = util.cos_sim(jd_embeddings, resume_embeddings)
    
    matched = set()
    missing = set()
    
    # For each JD requirement, find the best matching resume skill
    for i in range(len(jd_keywords)):
        max_score = cosine_scores[i].max().item()
        if max_score >= threshold:
            best_match_idx = cosine_scores[i].argmax().item()
            # Storing a tuple of (required text, what matched it in resume)
            matched.add(jd_keywords[i])
        else:
            missing.add(jd_keywords[i])
            
    return list(matched), list(missing)

def analyze_resume(pdf_bytes, job_url):
    nlp, sbert = load_models()
    
    resume_text = extract_text_from_pdf(pdf_bytes)
    jd_text, job_title = extract_text_from_url(job_url)
    
    if not resume_text or not jd_text:
        return {
            "score": 0,
            "error": "Failed to extract text from PDF or URL.",
            "job_title": job_title
        }
    
    # 1. Extract raw keyword phrases
    jd_keywords = extract_keywords(jd_text, nlp)
    resume_keywords = extract_keywords(resume_text, nlp)
    
    # Limit JD keywords to top 30 to keep execution fast and focused
    # (In a production app we'd use TF-IDF or an LLM to find the *most* important ones)
    jd_keywords = list(set(jd_keywords))[:30] 
    
    # 2. Semantic matching
    matched, missing = semantic_match(jd_keywords, resume_keywords, sbert)
    
    total = len(jd_keywords)
    score = int((len(matched) / total * 100)) if total > 0 else 0
    
    # 3. Generate actionable suggestions
    suggestions = []
    if missing:
        # Get top 3 isolated missing keywords to suggest
        top_missing = missing[:3]
        for m in top_missing:
            suggestions.append(f"Consider adding semantic equivalents of '{m.title()}' to your experience or skills section.")
            
        if score < 50:
            suggestions.append("Your resume currently lacks many key phrases found in the job description. Try tailoring your bullet points to tightly match the JD language.")
    
    return {
        "score": score,
        "job_title": job_title,
        "jd_text": jd_text,
        "resume_skills": [m.title() for m in matched[:10]], # show up to 10
        "missing_skills": [m.title() for m in missing[:10]], 
        "suggestions": suggestions
    }
