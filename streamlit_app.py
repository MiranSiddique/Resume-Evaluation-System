# streamlit_app.py
import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Configure Streamlit page
st.set_page_config(
    page_title="Resume Evaluation System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
#API_BASE_URL = "http://localhost:8000/api"

API_BASE_URL = "http://backend:8000/api"


# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #1f77b4;
    }
    .job-card {
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        background-color: #f8f9fa;
    }
    .score-excellent {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .score-good {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .score-average {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .score-below-average {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def get_job_postings(self):
        try:
            response = requests.get(f"{self.base_url}/job-postings/")
            return response.json() if response.status_code == 200 else []
        except:
            return []
    
    def create_job_posting(self, data):
        try:
            response = requests.post(f"{self.base_url}/job-postings/", json=data)
            return response.json() if response.status_code == 201 else None
        except:
            return None
    
    def update_job_posting(self, job_id, data):
        try:
            response = requests.put(f"{self.base_url}/job-postings/{job_id}/", json=data)
            return response.json() if response.status_code == 200 else None
        except:
            return None
    
    def upload_resume(self, file):
        try:
            files = {'file': file}
            response = requests.post(f"{self.base_url}/resumes/", files=files)
            return response.json() if response.status_code == 201 else None
        except:
            return None
    
    def update_resume_data(self, resume_id, data):
        try:
            response = requests.put(f"{self.base_url}/resumes/{resume_id}/update_extracted_data/", json=data)
            return response.json() if response.status_code == 200 else None
        except:
            return None
    
    def analyze_resume(self, resume_id, job_posting_id):
        try:
            data = {
                'resume_id': resume_id,
                'job_posting_id': job_posting_id
            }
            response = requests.post(f"{self.base_url}/evaluations/analyze/", json=data)
            return response.json() if response.status_code == 200 else None
        except:
            return None

def safe_format_salary(value):
    """Safely format salary value to float for display"""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def main():
    st.markdown('<h1 class="main-header"> Resume Evaluation System</h1>', unsafe_allow_html=True)
    
    # Initialize API client
    api = APIClient(API_BASE_URL)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", [
        "Job Details", 
        "Upload Resume", 
        "Review & Analyze", 
        "Results Dashboard"
    ])
    
    if page == "Job Details":
        show_job_details_page(api)
    elif page == "Upload Resume":
        show_upload_resume_page(api)
    elif page == "Review & Analyze":
        show_review_analyze_page(api)
    elif page == "Results Dashboard":
        show_results_dashboard(api)

def show_job_details_page(api):
    st.header(" Job Details Management")
    
    # Get existing job postings
    job_postings = api.get_job_postings()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Current Job Postings")
        if job_postings:
            for job in job_postings:
                with st.expander(f"{job['title']} - {job['department']}"):
                    st.write(f"**Location:** {job['location']}")
                    st.write(f"**Experience Required:** {job['experience_required']} years")
                    st.write(f"**Description:** {job['description']}")
                    st.write(f"**Required Skills:** {job['required_skills']}")
                    
                    # Safe salary formatting
                    salary_min = safe_format_salary(job.get('salary_min'))
                    salary_max = safe_format_salary(job.get('salary_max'))
                    
                    if salary_min is not None and salary_max is not None:
                        st.write(f"**Salary Range:** ${salary_min:,.0f} - ${salary_max:,.0f}")
                    elif salary_min is not None:
                        st.write(f"**Minimum Salary:** ${salary_min:,.0f}")
                    elif salary_max is not None:
                        st.write(f"**Maximum Salary:** ${salary_max:,.0f}")
                    
                    if st.button(f"Edit Job {job['id']}", key=f"edit_{job['id']}"):
                        st.session_state.editing_job = job
        else:
            st.info("No job postings found. Create one below.")
    
    with col2:
        st.subheader("Create/Edit Job Posting")
        
        # Check if we're editing
        editing_job = st.session_state.get('editing_job', None)
        
        with st.form("job_form"):
            title = st.text_input("Job Title", value=editing_job['title'] if editing_job else "")
            department = st.text_input("Department", value=editing_job['department'] if editing_job else "")
            location = st.text_input("Location", value=editing_job['location'] if editing_job else "")
            description = st.text_area("Job Description", 
                                     value=editing_job['description'] if editing_job else "",
                                     height=150)
            required_skills = st.text_area("Required Skills (comma-separated)", 
                                         value=editing_job['required_skills'] if editing_job else "",
                                         help="e.g., Python, Django, React, SQL")
            experience_required = st.number_input("Experience Required (years)", 
                                                min_value=0, max_value=20,
                                                value=editing_job['experience_required'] if editing_job else 0)
            
            col_sal1, col_sal2 = st.columns(2)
            with col_sal1:
                salary_min_default = 0.0
                if editing_job and editing_job.get('salary_min'):
                    salary_min_formatted = safe_format_salary(editing_job['salary_min'])
                    salary_min_default = salary_min_formatted if salary_min_formatted is not None else 0.0
                
                salary_min = st.number_input("Minimum Salary", value=salary_min_default)
                
            with col_sal2:
                salary_max_default = 0.0
                if editing_job and editing_job.get('salary_max'):
                    salary_max_formatted = safe_format_salary(editing_job['salary_max'])
                    salary_max_default = salary_max_formatted if salary_max_formatted is not None else 0.0
                
                salary_max = st.number_input("Maximum Salary", value=salary_max_default)
            
            submit_button = st.form_submit_button("Update Job" if editing_job else "Create Job")
            
            if submit_button:
                job_data = {
                    'title': title,
                    'department': department,
                    'location': location,
                    'description': description,
                    'required_skills': required_skills,
                    'experience_required': experience_required,
                    'salary_min': salary_min if salary_min > 0 else None,
                    'salary_max': salary_max if salary_max > 0 else None
                }
                
                if editing_job:
                    result = api.update_job_posting(editing_job['id'], job_data)
                    if result:
                        st.success("Job posting updated successfully!")
                        st.session_state.editing_job = None
                        st.rerun()
                    else:
                        st.error("Failed to update job posting")
                else:
                    result = api.create_job_posting(job_data)
                    if result:
                        st.success("Job posting created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create job posting")

def show_upload_resume_page(api):
    st.header(" Upload Resume")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a PDF resume file",
        type="pdf",
        help="Please upload a PDF resume following Jake's resume format"
    )
    
    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        
        if st.button("Process Resume", type="primary"):
            with st.spinner("Extracting data from resume..."):
                resume_data = api.upload_resume(uploaded_file)
                
                if resume_data:
                    st.session_state.current_resume = resume_data
                    st.success("Resume processed successfully!")
                    st.rerun()
                else:
                    st.error("Failed to process resume. Please try again.")
    
    # Show extracted data if available
    if 'current_resume' in st.session_state:
        st.subheader(" Extracted Information")
        st.info("Please review and correct the extracted information if needed.")
        
        resume = st.session_state.current_resume
        
        with st.form("resume_correction_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name", value=resume.get('name', ''))
                email = st.text_input("Email", value=resume.get('email', ''))
                phone = st.text_input("Phone", value=resume.get('phone', ''))
            
            with col2:
                education = st.text_area("Education", value=resume.get('education', ''), height=100)
                skills = st.text_area("Skills", value=resume.get('skills', ''), height=100)
            
            experience = st.text_area("Experience", value=resume.get('experience', ''), height=150)
            
            if st.form_submit_button("Update Information"):
                updated_data = {
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'education': education,
                    'experience': experience,
                    'skills': skills
                }
                
                result = api.update_resume_data(resume['id'], updated_data)
                if result:
                    st.session_state.current_resume = result
                    st.success("Resume information updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update resume information")

def show_review_analyze_page(api):
    st.header(" Review & Analyze Resume")
    
    if 'current_resume' not in st.session_state:
        st.warning("Please upload a resume first!")
        return
    
    # Get job postings
    job_postings = api.get_job_postings()
    
    if not job_postings:
        st.warning("Please create a job posting first!")
        return
    
    st.subheader("Select Job Posting")
    job_options = {f"{job['title']} - {job['department']}": job['id'] for job in job_postings}
    selected_job_title = st.selectbox("Choose a job posting to analyze against:", list(job_options.keys()))
    
    if selected_job_title:
        selected_job_id = job_options[selected_job_title]
        selected_job = next(job for job in job_postings if job['id'] == selected_job_id)
        
        # Show job details
        with st.expander(" Job Details", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Title:** {selected_job['title']}")
                st.write(f"**Department:** {selected_job['department']}")
                st.write(f"**Location:** {selected_job['location']}")
                st.write(f"**Experience Required:** {selected_job['experience_required']} years")
            with col2:
                st.write(f"**Required Skills:** {selected_job['required_skills']}")
                
                # Safe salary display
                salary_min = safe_format_salary(selected_job.get('salary_min'))
                salary_max = safe_format_salary(selected_job.get('salary_max'))
                
                if salary_min is not None and salary_max is not None:
                    st.write(f"**Salary Range:** ${salary_min:,.0f} - ${salary_max:,.0f}")
                elif salary_min is not None:
                    st.write(f"**Minimum Salary:** ${salary_min:,.0f}")
                elif salary_max is not None:
                    st.write(f"**Maximum Salary:** ${salary_max:,.0f}")
            
            st.write(f"**Description:** {selected_job['description']}")
        
        # Show resume summary
        resume = st.session_state.current_resume
        with st.expander("👤 Resume Summary", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Name:** {resume.get('name', 'N/A')}")
                st.write(f"**Email:** {resume.get('email', 'N/A')}")
                st.write(f"**Phone:** {resume.get('phone', 'N/A')}")
            with col2:
                st.write(f"**Skills:** {resume.get('skills', 'N/A')}")
            
            if resume.get('education'):
                st.write(f"**Education:** {resume['education']}")
            if resume.get('experience'):
                st.write(f"**Experience:** {resume['experience']}")
        
        # Analyze button
        if st.button(" Analyze Resume", type="primary", use_container_width=True):
            with st.spinner("Analyzing resume... This may take a few moments."):
                evaluation = api.analyze_resume(resume['id'], selected_job_id)
                
                if evaluation:
                    st.session_state.current_evaluation = evaluation
                    st.success("Analysis completed!")
                    st.rerun()
                else:
                    st.error("Failed to analyze resume. Please try again.")

def show_results_dashboard(api):
    st.header("Results Dashboard")
    
    if 'current_evaluation' not in st.session_state:
        st.warning("Please analyze a resume first!")
        return
    
    evaluation = st.session_state.current_evaluation
    
    # Overall Score Card
    st.subheader(" Overall Score")
    
    col1, col2, col3, col4 = st.columns(4)
    
    final_score = evaluation['final_score']
    category = evaluation['category']
    
    with col1:
        st.metric("Final Score", f"{final_score:.1f}/100")
    
    with col2:
        category_display = {
            'excellent': 'Excellent',
            'good': 'Good', 
            'average': 'Average',
            'below_average': 'Below Average'
        }
        st.metric("Category", category_display[category])
    
    with col3:
        st.metric("Skill Match", f"{evaluation['skill_match_score']:.1f}%")
    
    with col4:
        st.metric("Experience Score", f"{evaluation['experience_score']:.1f}%")
    
    # Score breakdown chart
    st.subheader(" Score Breakdown")
    
    scores_data = {
        'Category': ['Skill Match', 'Experience', 'Education', 'Text Similarity'],
        'Score': [
            evaluation['skill_match_score'],
            evaluation['experience_score'], 
            evaluation['education_score'],
            evaluation['cosine_similarity_score']
        ]
    }
    
    fig = px.bar(
        scores_data, 
        x='Category', 
        y='Score',
        title='Detailed Score Analysis',
        color='Score',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Skills analysis
    st.subheader("🔧 Skills Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**✅ Matched Skills**")
        try:
            matched_skills = json.loads(evaluation['matched_skills'])
            if matched_skills:
                for skill in matched_skills:
                    st.success(f"✓ {skill}")
            else:
                st.info("No specific skill matches found")
        except:
            st.info("No skill match data available")
    
    with col2:
        st.write("**❌ Missing Skills**")
        try:
            missing_skills = json.loads(evaluation['missing_skills'])
            if missing_skills:
                for skill in missing_skills:
                    st.error(f"✗ {skill}")
            else:
                st.success("All required skills matched!")
        except:
            st.info("No missing skill data available")
    
    # Keyword highlights
    st.subheader("🔍 Key Matching Keywords")
    try:
        keywords = json.loads(evaluation['keyword_highlights'])
        if keywords:
            keyword_cols = st.columns(min(len(keywords), 5))
            for i, keyword in enumerate(keywords):
                with keyword_cols[i % 5]:
                    st.info(f"🎯 {keyword}")
        else:
            st.info("No significant keyword matches found")
    except:
        st.info("No keyword data available")
    
    # Recommendations
    st.subheader("💡 Recommendations")
    
    if final_score >= 80:
        st.markdown('<div class="score-excellent"> Excellent match! This candidate shows strong alignment with the job requirements.</div>', unsafe_allow_html=True)
    elif final_score >= 60:
        st.markdown('<div class="score-good"> Good match! This candidate meets most of the job requirements with minor gaps.</div>', unsafe_allow_html=True)
    elif final_score >= 40:
        st.markdown('<div class="score-average"> Average match. This candidate has some relevant qualifications but significant skill gaps exist.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="score-below-average"> Below average match. This candidate may need significant development to meet job requirements.</div>', unsafe_allow_html=True)
    
    # Detailed recommendations based on scores
    recommendations = []
    
    if evaluation['skill_match_score'] < 60:
        recommendations.append(" **Skills Development**: Consider training in missing technical skills")
    
    if evaluation['experience_score'] < 60:
        recommendations.append(" **Experience**: Look for candidates with more relevant work experience")
    
    if evaluation['education_score'] < 60:
        recommendations.append(" **Education**: Consider educational background relevance")
    
    if recommendations:
        st.write("**Specific Recommendations:**")
        for rec in recommendations:
            st.write(f"• {rec}")

if __name__ == "__main__":
    if 'current_resume' not in st.session_state:
        st.session_state.current_resume = None
    if 'current_evaluation' not in st.session_state:
        st.session_state.current_evaluation = None
    if 'editing_job' not in st.session_state:
        st.session_state.editing_job = None
    
    main()