import PyPDF2
import re
from io import BytesIO

class ResumeExtractor:
    def __init__(self):
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        
    def extract_text_from_pdf(self, pdf_file):
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error extracting PDF: {str(e)}")
    
    def extract_contact_info(self, text):
        lines = text.split('\n')
        contact_info = {'name': '', 'email': '', 'phone': ''}
        
        # Extract email
        email_match = re.search(self.email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group()
        
        # Extract phone
        phone_match = re.search(self.phone_pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group()
        
        # Extract name (usually first non-empty line)
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and not re.search(self.email_pattern, line) and not re.search(self.phone_pattern, line):
                if len(line.split()) >= 2 and len(line) < 50:  # Likely a name
                    contact_info['name'] = line
                    break
        
        return contact_info
    
    def extract_education(self, text):
        education_keywords = ['education', 'degree', 'university', 'college', 'bachelor', 'master', 'phd', 'diploma']
        lines = text.lower().split('\n')
        
        education_section = []
        in_education_section = False
        
        for i, line in enumerate(lines):
            if any(keyword in line for keyword in education_keywords):
                in_education_section = True
                # Get next few lines as education details
                for j in range(i, min(i+10, len(lines))):
                    if lines[j].strip():
                        education_section.append(lines[j].strip())
                break
        
        return '\n'.join(education_section[:5]) if education_section else ''
    
    def extract_experience(self, text):
        experience_keywords = ['experience', 'work', 'employment', 'career', 'position', 'job']
        lines = text.lower().split('\n')
        
        experience_section = []
        in_experience_section = False
        
        for i, line in enumerate(lines):
            if any(keyword in line for keyword in experience_keywords):
                in_experience_section = True
                # Get next several lines as experience details
                for j in range(i, min(i+15, len(lines))):
                    if lines[j].strip():
                        experience_section.append(lines[j].strip())
                break
        
        return '\n'.join(experience_section[:10]) if experience_section else ''
    
    def extract_skills(self, text):
        skills_keywords = ['skills', 'technical skills', 'technologies', 'programming', 'tools']
        lines = text.lower().split('\n')
        
        skills_section = []
        
        for i, line in enumerate(lines):
            if any(keyword in line for keyword in skills_keywords):
                # Get next few lines as skills
                for j in range(i+1, min(i+8, len(lines))):
                    if lines[j].strip() and not any(kw in lines[j] for kw in ['experience', 'education', 'project']):
                        skills_section.append(lines[j].strip())
                break
        
        # Clean and format skills
        skills_text = ' '.join(skills_section)
        skills_text = re.sub(r'[•·\-\*]', ',', skills_text)
        skills_text = re.sub(r'\s+', ' ', skills_text)
        
        return skills_text
    
    def extract_all_data(self, pdf_file):
        text = self.extract_text_from_pdf(pdf_file)
        
        contact_info = self.extract_contact_info(text)
        education = self.extract_education(text)
        experience = self.extract_experience(text)
        skills = self.extract_skills(text)
        
        return {
            'raw_text': text,
            'name': contact_info['name'],
            'email': contact_info['email'],
            'phone': contact_info['phone'],
            'education': education,
            'experience': experience,
            'skills': skills
        }