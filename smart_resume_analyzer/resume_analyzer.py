import streamlit as st
import re
import difflib

# =============================================================================
# 1. NLP & TEXT PROCESSING ENGINE
# =============================================================================

# A comprehensive dictionary of common tech and professional skills to search for.
SKILL_DATABASE = [
    # Programming Languages
    "python", "java", "javascript", "c++", "c#", "ruby", "go", "rust", "php", "swift", "kotlin", "typescript",
    # Web Development
    "html", "css", "react", "angular", "vue", "node.js", "django", "flask", "fastapi", "spring boot", "express",
    # Data & AI
    "sql", "mysql", "postgresql", "mongodb", "machine learning", "deep learning", "nlp", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "data analysis",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "github", "ci/cd", "linux",
    # Soft Skills
    "communication", "leadership", "teamwork", "problem solving", "agile", "scrum", "project management"
]

def clean_text(text):
    """Converts text to lowercase and removes special characters."""
    text = text.lower()
    # Keep only alphanumeric characters and spaces
    text = re.sub(r'[^a-z0-9\s+#]', ' ', text)
    return text

def extract_skills(text):
    """Finds skills from the database within the provided text."""
    cleaned_text = clean_text(text)
    found_skills = set()
    
    for skill in SKILL_DATABASE:
        # Use word boundaries to prevent matching parts of words (e.g., 'go' in 'good')
        # Special handling for skills with special characters like C++ or C#
        if skill in ["c++", "c#"]:
            if skill in cleaned_text:
                found_skills.add(skill)
        else:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, cleaned_text):
                found_skills.add(skill)
                
    return found_skills

def calculate_similarity(resume_text, jd_text):
    """Calculates a basic text similarity score using SequenceMatcher."""
    # This is a basic string-matching algorithm (not deep semantic meaning)
    matcher = difflib.SequenceMatcher(None, resume_text.lower(), jd_text.lower())
    return round(matcher.ratio() * 100, 2)

# =============================================================================
# 2. STREAMLIT UI
# =============================================================================
st.set_page_config(page_title="Smart Resume Analyzer", page_icon="📄", layout="wide")

st.title("📄 Smart Resume Analyzer")
st.markdown("""
**What it does:**
Analyzes a resume against a job description and finds matching and missing skills using NLP.
""")

# Sidebar Configuration
with st.sidebar:
    st.header("💡 How to use")
    st.info("""
    1. Paste the Job Description in the left box.
    2. Paste your Resume text in the right box.
    3. Click 'Analyze Match'.
    
    *Note: For best results, paste the raw text of your PDF resume rather than an image.*
    """)
    
    with st.expander("⚙️ See NLP Logic"):
        st.write("This app uses Regular Expressions (`re`) to clean text and match over 40 predefined industry skills. It also uses Python's `difflib` to calculate a text similarity score.")

# Main Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Job Description")
    jd_input = st.text_area(
        "Paste the job description here:", 
        height=400,
        placeholder="We are looking for a Python Developer with experience in FastAPI, SQL, and AWS..."
    )

with col2:
    st.subheader("📄 Your Resume")
    resume_input = st.text_area(
        "Paste your resume text here:", 
        height=400,
        placeholder="Experienced Software Engineer skilled in Python, Django, and Docker..."
    )

st.divider()

# Analysis Button
if st.button("🔍 Analyze Match", type="primary", use_container_width=True):
    if not jd_input.strip() or not resume_input.strip():
        st.warning("Please provide both a Job Description and a Resume.")
    else:
        # 1. Run NLP extraction
        jd_skills = extract_skills(jd_input)
        resume_skills = extract_skills(resume_input)
        
        # 2. Calculate Skill Matching
        matched_skills = jd_skills.intersection(resume_skills)
        missing_skills = jd_skills - resume_skills
        extra_skills = resume_skills - jd_skills
        
        # 3. Calculate Similarity Score
        similarity_score = calculate_similarity(resume_input, jd_input)
        
        # --- DISPLAY RESULTS ---
        st.header("📊 Analysis Results")
        
        # Top Metrics
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Skill Match Rate", f"{len(matched_skills)} / {len(jd_skills)}")
        metric_col2.metric("Text Similarity", f"{similarity_score}%")
        
        # Calculate a combined "Fit Score"
        skill_score = (len(matched_skills) / len(jd_skills) * 100) if jd_skills else 0
        final_score = (skill_score * 0.7) + (similarity_score * 0.3) # Weighted average
        metric_col3.metric("Overall Fit Score", f"{final_score:.1f}%", delta=None)
        
        st.progress(int(final_score), text="Overall Candidate Fit")
        
        st.divider()
        
        # Skill Breakdown (Lists)
        res_col1, res_col2 = st.columns(2)
        
        with res_col1:
            st.subheader("✅ Matched Skills")
            if matched_skills:
                st.success(", ".join(sorted(matched_skills)).title())
            else:
                st.info("No specific technical skills matched.")
                
            st.subheader("🌟 Extra Skills (Bonus)")
            if extra_skills:
                st.write(", ".join(sorted(extra_skills)).title())
                
        with res_col2:
            st.subheader("❌ Missing Skills (Gaps)")
            if missing_skills:
                st.error(", ".join(sorted(missing_skills)).title())
                st.caption("Consider adding these keywords to your resume if you have experience with them.")
            else:
                st.success("You have all the required skills!")
        
        # --- BONUS: Downloadable Report ---
        st.divider()
        report_text = f"""
        SMART RESUME ANALYZER REPORT
        ----------------------------
        Overall Fit Score: {final_score:.1f}%
        Text Similarity: {similarity_score}%
        
        MATCHED SKILLS:
        {', '.join(sorted(matched_skills)).title() if matched_skills else 'None'}
        
        MISSING SKILLS:
        {', '.join(sorted(missing_skills)).title() if missing_skills else 'None'}
        
        BONUS SKILLS:
        {', '.join(sorted(extra_skills)).title() if extra_skills else 'None'}
        """
        st.download_button(
            label="📥 Download Analysis Report",
            data=report_text,
            file_name="resume_analysis.txt",
            mime="text/plain"
        )