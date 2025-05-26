# 📄 Resume Evaluation System

An intelligent resume screening and evaluation system that automatically analyzes resumes against job postings using advanced NLP techniques and machine learning algorithms.

https://github.com/user-attachments/assets/99001283-28d2-4623-a1f5-7f1ed46801a2

## Features

- **Automated PDF Resume Processing**: Extract structured data from PDF resumes
- **Intelligent Job Matching**: Multi-faceted evaluation using skill matching, experience analysis, and semantic similarity
- **Interactive Dashboard**: Streamlit interface for HR managers
- **Real-time Analysis**: Instant resume evaluation with detailed scoring breakdown
- **Skill Gap Analysis**: Identify matched and missing skills with actionable recommendations
- **RESTful API**: Complete Django REST API for integration with existing systems
- **Weighted Scoring Algorithm**: Configurable scoring weights based on hiring priorities

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│    Streamlit    │    │   Django REST    │    │     SQLite      │
│    Frontend     │◄──►│      API         │◄──►│    Database     │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Processing Utils │
                       │                  │
                       │ • PDF Extractor  │
                       │ • Resume         │
                       │   Evaluator      │
                       │                  │
                       └──────────────────┘
```

## Quick Setup with Docker

```bash
# Clone the repository
git clone https://github.com/your-username/resume-evaluator.git
cd resume-evaluator

# Build and run the entire system
docker-compose up --build
```

The system will be available at:
- **Streamlit App**: http://localhost:8501
- **Django API**: http://localhost:8000


## Manual Installation (Without Docker)

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-backend.txt

# Setup database
python manage.py migrate
python manage.py createsuperuser

# Run server
python manage.py runserver
```

### Frontend Setup

```bash
# In a new terminal
pip install -r requirements-frontend.txt

# Update API_BASE_URL in streamlit_app.py to http://localhost:8000/api

# Run Streamlit
streamlit run streamlit_app.py
```

## Usage Guide

### 1. Create Job Posting

1. Navigate to **Job Details** page
2. Fill in job requirements:
   - Job title and department
   - Required skills (comma-separated)
   - Experience requirements
   - Job description
3. Click **Create Job**

### 2. Upload Resume

1. Go to **Upload Resume** page
2. Upload PDF resume file
3. Review and correct extracted information
4. Save updated information

### 3. Analyze Resume

1. Visit **Review & Analyze** page
2. Select job posting to compare against
3. Review job and resume details
4. Click **Analyze Resume**

### 4. View Results

1. Check **Results Dashboard** for:
   - Overall compatibility score
   - Detailed score breakdown
   - Skill gap analysis
   - Actionable recommendations

## Algorithm Details

### Scoring Components

1. **Skill Match (40%)**: Fuzzy matching between resume and job skills
2. **Experience (30%)**: Years of experience vs. requirements
3. **Education (20%)**: Educational background relevance
4. **Text Similarity (10%)**: Semantic similarity using TF-IDF

### Score Categories

- **Excellent (80-100)**: Strong match, recommend for interview
- **Good (60-79)**: Good match with minor gaps
- **Average (40-59)**: Some qualifications, significant gaps
- **Below Average (0-39)**: Poor match, major deficiencies

## API Endpoints

### Job Postings
- `GET /api/job-postings/` - List all job postings
- `POST /api/job-postings/` - Create new job posting
- `PUT /api/job-postings/{id}/` - Update job posting

### Resumes
- `GET /api/resumes/` - List all resumes
- `POST /api/resumes/` - Upload resume
- `PUT /api/resumes/{id}/update_extracted_data/` - Update extracted data

### Evaluations
- `POST /api/evaluations/analyze/` - Analyze resume against job posting
- `GET /api/evaluations/` - List all evaluations

## Acknowledgments

- Built with Django REST Framework and Streamlit
- PDF processing powered by PyPDF2
- Machine learning with scikit-learn
- UI components from Plotly

