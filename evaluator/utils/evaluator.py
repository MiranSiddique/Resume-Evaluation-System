import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

class ResumeEvaluator:
    def __init__(self):
        self.skill_weight = 0.4
        self.experience_weight = 0.3
        self.education_weight = 0.2
        self.cosine_weight = 0.1
    
    def normalize_text(self, text):
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def calculate_skill_match(self, resume_skills, job_skills):
        resume_skills_normalized = [self.normalize_text(skill) for skill in resume_skills]
        job_skills_normalized = [self.normalize_text(skill) for skill in job_skills]
        
        matched_skills = []
        for job_skill in job_skills_normalized:
            for resume_skill in resume_skills_normalized:
                if job_skill in resume_skill or resume_skill in job_skill:
                    matched_skills.append(job_skill)
                    break
        
        missing_skills = [skill for skill in job_skills_normalized if skill not in matched_skills]
        
        if not job_skills_normalized:
            return 0, [], missing_skills
        
        match_percentage = (len(matched_skills) / len(job_skills_normalized)) * 100
        return match_percentage, matched_skills, missing_skills
    
    def calculate_experience_score(self, resume_text, required_years):
        # Extract years of experience from resume
        year_pattern = r'(\d+)\s*(?:years?|yrs?)'
        years_found = re.findall(year_pattern, resume_text.lower())
        
        if years_found:
            max_years = max([int(year) for year in years_found])
            if max_years >= required_years:
                return 100
            else:
                return (max_years / required_years) * 100
        
        # If no specific years mentioned, look for experience keywords
        experience_keywords = ['experience', 'worked', 'developed', 'managed', 'led', 'created']
        keyword_count = sum(1 for keyword in experience_keywords if keyword in resume_text.lower())
        
        return min(keyword_count * 15, 70)  # Cap at 70 if no specific years
    
    def calculate_education_score(self, resume_education, job_description):
        education_keywords = ['degree', 'bachelor', 'master', 'phd', 'diploma', 'certification']
        resume_edu_lower = resume_education.lower()
        job_desc_lower = job_description.lower()
        
        score = 0
        
        # Check for degree mentions
        if any(keyword in resume_edu_lower for keyword in education_keywords):
            score += 50
        
        # Check for relevant field mentions
        if 'computer' in resume_edu_lower or 'software' in resume_edu_lower:
            score += 30
        
        # Check if job requires specific education
        if any(keyword in job_desc_lower for keyword in education_keywords):
            if any(keyword in resume_edu_lower for keyword in education_keywords):
                score += 20
        
        return min(score, 100)
    
    def calculate_cosine_similarity(self, resume_text, job_description):
        try:
            documents = [self.normalize_text(resume_text), self.normalize_text(job_description)]
            
            vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
            tfidf_matrix = vectorizer.fit_transform(documents)
            
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity * 100
        except:
            return 0
    
    def extract_keyword_highlights(self, resume_text, job_description):
        try:
            vectorizer = TfidfVectorizer(stop_words='english', max_features=50, ngram_range=(1, 2))
            job_vector = vectorizer.fit_transform([self.normalize_text(job_description)])
            
            feature_names = vectorizer.get_feature_names_out()
            job_scores = job_vector.toarray()[0]
            
            # Get top keywords from job description
            top_job_keywords = [feature_names[i] for i in job_scores.argsort()[-10:][::-1]]
            
            # Find which keywords appear in resume
            resume_lower = self.normalize_text(resume_text)
            matched_keywords = [keyword for keyword in top_job_keywords if keyword in resume_lower]
            
            return matched_keywords[:5]  # Return top 5 matches
        except:
            return []
    
    def evaluate_resume(self, resume, job_posting):
        # Rule-based analysis
        skill_score, matched_skills, missing_skills = self.calculate_skill_match(
            resume.skills_list, job_posting.skills_list
        )
        
        experience_score = self.calculate_experience_score(
            resume.raw_text, job_posting.experience_required
        )
        
        education_score = self.calculate_education_score(
            resume.education, job_posting.description
        )
        
        # Cosine similarity
        cosine_score = self.calculate_cosine_similarity(
            resume.raw_text, job_posting.description
        )
        
        # Calculate weighted final score
        final_score = (
            skill_score * self.skill_weight +
            experience_score * self.experience_weight +
            education_score * self.education_weight +
            cosine_score * self.cosine_weight
        )
        
        # Get keyword highlights
        keyword_highlights = self.extract_keyword_highlights(
            resume.raw_text, job_posting.description
        )
        
        # Determine category
        category = self.get_category_from_score(final_score)
        
        return {
            'skill_match_score': skill_score,
            'experience_score': experience_score,
            'education_score': education_score,
            'cosine_similarity_score': cosine_score,
            'final_score': final_score,
            'category': category,
            'matched_skills': json.dumps(matched_skills),
            'missing_skills': json.dumps(missing_skills),
            'keyword_highlights': json.dumps(keyword_highlights)
        }
    
    def get_category_from_score(self, score):
        if score >= 80:
            return 'excellent'
        elif score >= 60:
            return 'good'
        elif score >= 40:
            return 'average'
        else:
            return 'below_average'