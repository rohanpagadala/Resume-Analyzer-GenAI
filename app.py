import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_extras.add_vertical_space import add_vertical_space
import PyPDF2
import os
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Resume Analyzer & LinkedIn Scraper",
    page_icon="📄",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #333;
        margin-bottom: 1rem;
    }
    .feature-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 2px solid #e9ecef;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .feature-box p {
        color: #212529;
        font-size: 16px;
        line-height: 1.6;
        margin-bottom: 0.8rem;
    }
    .feature-box strong {
        color: #0d6efd;
        font-weight: 600;
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid #2196f3;
        margin: 1rem 0;
    }
    .info-box p {
        color: #1565c0;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    .result-box {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
    }
    .warning-box {
        background-color: #fff8e1;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ff9800;
        color: #e65100;
        font-weight: 500;
    }
    .error-box {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #f44336;
        color: #c62828;
        font-weight: 500;
    }
    
    /* Better button styling */
    .stButton > button {
        background-color: #0d6efd;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #0b5ed7;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* File uploader styling */
    .uploadedFile {
        background-color: #f8f9fa;
        border: 2px dashed #6c757d;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
    }
    
    /* Sidebar improvements */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Success message styling */
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    /* Job card styling */
    .job-card {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .job-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    .job-title {
        color: #0d6efd;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .company-name {
        color: #6c757d;
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 0.3rem;
    }
    
    .success-box {
        background-color: #e8f5e8;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.15);
    }
    .success-box h3 {
        color: #2e7d32;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return None

def analyze_resume_with_gemini(resume_text, query, api_key):
    """Analyze resume using Google Gemini API"""
    try:
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # Initialize the model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        You are an expert career counselor and resume analyst. Provide detailed, actionable feedback.
        
        Based on the following resume content, please {query}
        
        Resume Content:
        {resume_text[:6000]}  # Gemini can handle more text than GPT-3.5
        
        Please provide a detailed and helpful response.
        """
        
        # Generate response
        response = model.generate_content(prompt)
        
        return response.text
    except Exception as e:
        st.error(f"Error analyzing resume: {str(e)}")
        return None

def setup_selenium_driver():
    """Setup Selenium WebDriver for LinkedIn scraping"""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        return driver
    except Exception as e:
        st.error(f"Error setting up web driver: {str(e)}")
        return None

def scrape_linkedin_jobs(job_title, location="", num_jobs=10):
    """Scrape LinkedIn jobs using Selenium"""
    try:
        driver = setup_selenium_driver()
        if not driver:
            return None
        
        # Construct LinkedIn job search URL
        base_url = "https://www.linkedin.com/jobs/search"
        search_url = f"{base_url}?keywords={job_title.replace(' ', '%20')}"
        if location:
            search_url += f"&location={location.replace(' ', '%20')}"
        
        driver.get(search_url)
        time.sleep(3)
        
        jobs_data = []
        
        # Find job listings
        job_cards = driver.find_elements(By.CSS_SELECTOR, ".job-search-card")
        
        for i, card in enumerate(job_cards[:num_jobs]):
            try:
                # Extract job details
                title_element = card.find_element(By.CSS_SELECTOR, ".base-search-card__title")
                company_element = card.find_element(By.CSS_SELECTOR, ".base-search-card__subtitle")
                location_element = card.find_element(By.CSS_SELECTOR, ".job-search-card__location")
                link_element = card.find_element(By.CSS_SELECTOR, "a")
                
                job_data = {
                    "Title": title_element.text.strip(),
                    "Company": company_element.text.strip(),
                    "Location": location_element.text.strip(),
                    "URL": link_element.get_attribute("href")
                }
                
                # Get job description (simplified)
                job_data["Description"] = "Click the URL to view full job description"
                
                jobs_data.append(job_data)
                
            except Exception:
                continue
        
        driver.quit()
        return jobs_data
        
    except Exception as e:
        st.error(f"Error scraping LinkedIn jobs: {str(e)}")
        return None

def get_resume_job_match_score(resume_text, job_description, api_key):
    """Generate semantic AI matching score between resume and job description"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        You are an AI recruitment expert. Perform a semantic analysis to match this resume with the job description.
        
        RESUME CONTENT:
        {resume_text[:4000]}
        
        JOB DESCRIPTION:
        {job_description[:3000]}
        
        Provide a detailed analysis in the following format:
        
        OVERALL MATCH SCORE: [X]%
        
        SKILL MATCH ANALYSIS:
        - Direct Skills Match: [X]% (skills that exactly match)
        - Related Skills Match: [X]% (similar/transferable skills)
        - Missing Critical Skills: [list key missing skills]
        
        EXPERIENCE RELEVANCE:
        - Years of Experience Match: [X]%
        - Domain Experience: [X]%
        - Role Suitability: [X]%
        
        STRENGTHS FOR THIS ROLE:
        - [List 3-4 key strengths from resume that match this job]
        
        IMPROVEMENT AREAS:
        - [List specific skills/experience to develop for this role]
        
        RECOMMENDATIONS:
        - [3-4 specific actionable recommendations to improve match]
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error in job matching analysis: {str(e)}")
        return None

def generate_tailored_resume(resume_text, job_description, api_key):
    """Generate job-specific tailored resume content"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        You are an expert resume writer. Create a tailored version of this resume for the specific job.
        
        ORIGINAL RESUME:
        {resume_text[:4000]}
        
        TARGET JOB:
        {job_description[:3000]}
        
        Generate optimized sections:
        
        TAILORED PROFESSIONAL SUMMARY:
        [Write a 3-4 line summary optimized for this job, highlighting most relevant skills and experience]
        
        OPTIMIZED SKILLS SECTION:
        [Reorder and enhance skills to match job requirements. Add related skills if missing.]
        
        ENHANCED PROJECT/EXPERIENCE DESCRIPTIONS:
        [Rewrite 2-3 key experiences/projects with job-relevant keywords and metrics]
        
        ATS OPTIMIZATION KEYWORDS:
        [List 10-15 keywords from job description to incorporate]
        
        SUGGESTED ADDITIONS:
        [Recommend any certifications, skills, or experiences to add for better job fit]
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error in resume tailoring: {str(e)}")
        return None

def generate_skill_gap_analysis(resume_text, job_description, api_key):
    """Analyze skill gaps and generate learning path"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        You are a career development expert. Analyze skill gaps and create a learning roadmap.
        
        CURRENT RESUME:
        {resume_text[:4000]}
        
        TARGET JOB:
        {job_description[:3000]}
        
        Provide analysis in this format:
        
        SKILL GAP ANALYSIS:
        
        MISSING CRITICAL SKILLS:
        - [List 3-5 most important missing skills]
        
        WEAK AREAS TO STRENGTHEN:
        - [List 2-3 skills present but need improvement]
        
        PERSONALIZED LEARNING PATH:
        
        PRIORITY 1 (Next 4 weeks):
        - Week 1: [Specific skill/topic to learn]
        - Week 2: [Next skill/topic]
        - Week 3: [Continue with next priority]
        - Week 4: [Practice/project week]
        
        PRIORITY 2 (Next 2 months):
        - Month 1: [Advanced topics]
        - Month 2: [Certification/project]
        
        RECOMMENDED RESOURCES:
        - Online Courses: [Suggest 2-3 specific courses]
        - Certifications: [Relevant certifications to pursue]
        - Practice Projects: [2-3 project ideas to build skills]
        
        SKILL DEVELOPMENT TIMELINE:
        - 30 days: [Expected skill level]
        - 60 days: [Expected skill level]
        - 90 days: [Job-ready assessment]
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error in skill gap analysis: {str(e)}")
        return None

def generate_interview_questions(resume_text, job_description, api_key):
    """Generate job-specific interview questions based on resume and job"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        You are an experienced interviewer. Generate interview questions for this candidate based on their resume and the target job.
        
        CANDIDATE RESUME:
        {resume_text[:4000]}
        
        TARGET JOB:
        {job_description[:3000]}
        
        Generate questions in these categories:
        
        TECHNICAL QUESTIONS (Based on Resume Experience):
        1. [Question about specific technology mentioned in resume]
        2. [Question about project details from resume]
        3. [Question about technical skills listed]
        4. [Scenario-based technical question]
        5. [Problem-solving question related to job requirements]
        
        BEHAVIORAL QUESTIONS (STAR Method):
        1. [Question about leadership/teamwork from resume]
        2. [Question about challenges/achievements mentioned]
        3. [Question about learning/adaptation]
        4. [Question about conflict resolution]
        
        JOB-SPECIFIC QUESTIONS:
        1. [Question about specific job requirement]
        2. [Question about company/industry knowledge needed]
        3. [Question about future goals in this role]
        
        SUGGESTED STAR METHOD ANSWERS:
        [Provide framework answers for 2-3 behavioral questions based on resume content]
        
        TECHNICAL PREPARATION AREAS:
        [List 5-7 technical topics to review based on job requirements]
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating interview questions: {str(e)}")
        return None

def check_ats_compatibility(resume_text, api_key):
    """Check ATS compatibility and suggest improvements"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        You are an ATS (Applicant Tracking System) expert. Analyze this resume for ATS compatibility.
        
        RESUME CONTENT:
        {resume_text[:5000]}
        
        Provide analysis in this format:
        
        ATS COMPATIBILITY SCORE: [X]/100
        
        SECTION ANALYSIS:
        
        ✅ GOOD PRACTICES FOUND:
        - [List what's working well]
        
        ❌ ATS ISSUES DETECTED:
        - [List specific formatting/content issues]
        
        KEYWORD OPTIMIZATION:
        - Keyword Density: [Assessment]
        - Missing Industry Keywords: [List important missing keywords]
        - Overused Keywords: [List if any]
        
        FORMATTING RECOMMENDATIONS:
        - [Specific formatting improvements needed]
        
        SECTION IMPROVEMENTS:
        - Contact Information: [Issues/suggestions]
        - Professional Summary: [Issues/suggestions]
        - Skills Section: [Issues/suggestions]
        - Experience Section: [Issues/suggestions]
        
        ATS-OPTIMIZED SUGGESTIONS:
        - [3-5 specific actionable improvements]
        
        REWRITTEN SECTIONS (if needed):
        [Provide ATS-friendly rewrites of problematic sections]
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error in ATS compatibility check: {str(e)}")
        return None

def generate_career_recommendations(resume_text, api_key):
    """Generate alternative career path recommendations"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        You are a career counselor. Analyze this resume and suggest alternative career paths and roles.
        
        RESUME CONTENT:
        {resume_text[:4000]}
        
        Provide recommendations in this format:
        
        CURRENT PROFILE ANALYSIS:
        - Primary Skills: [Top 5 skills]
        - Experience Level: [Assessment]
        - Industry Background: [Current industry/domain]
        
        RECOMMENDED CAREER PATHS:
        
        PATH 1: [Similar Role Progression]
        - Suggested Role: [Job title]
        - Why it fits: [Reasoning based on skills/experience]
        - Skills to develop: [2-3 skills needed]
        - Salary range: [Estimate if possible]
        
        PATH 2: [Lateral Move]
        - Suggested Role: [Job title]
        - Why it fits: [Reasoning]
        - Skills to develop: [2-3 skills needed]
        - Transition timeline: [Estimated time]
        
        PATH 3: [Growth/Advancement]
        - Suggested Role: [Senior/lead position]
        - Why it fits: [Reasoning]
        - Skills to develop: [Leadership/advanced skills]
        - Experience needed: [Additional requirements]
        
        EMERGING OPPORTUNITIES:
        - [2-3 trending roles that match profile]
        
        SKILL TRANSFERABILITY:
        - [How current skills apply to different industries]
        
        NEXT STEPS:
        - Immediate (30 days): [Action items]
        - Short-term (3 months): [Development goals]
        - Long-term (1 year): [Career milestone]
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating career recommendations: {str(e)}")
        return None

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Resume Analyzer & LinkedIn Scraper</h1>', unsafe_allow_html=True)
    
    # Sidebar for navigation
    with st.sidebar:
        st.title("Navigation")
        selected = option_menu(
            menu_title=None,
            options=["Resume Analyzer", "🚀 AI Job Matching", "🎨 Resume Tailoring", "📚 Skill Gap Analysis", 
                    "🎯 Interview Prep", "🔍 ATS Checker", "📈 Career Paths", "LinkedIn Scraper", "About"],
            icons=["file-earmark-text", "bullseye", "brush", "book", "chat-dots", 
                   "search", "graph-up", "linkedin", "info-circle"],
            menu_icon="cast",
            default_index=0,
        )
        
        add_vertical_space(3)
        
        # API Key handling
        st.markdown("### 🔑 Google Gemini API Key")
        
        # Check if API key is already in environment
        env_api_key = os.getenv("GEMINI_API_KEY")
        
        if env_api_key:
            st.success("✅ API Key loaded from environment file")
            api_key = env_api_key
        else:
            st.info("💡 Enter your API key below or add it to .env file")
            api_key = st.text_input("Enter your Google Gemini API Key", type="password")
            
            if api_key:
                os.environ["GEMINI_API_KEY"] = api_key
    
    # Resume Analyzer Tab
    if selected == "Resume Analyzer":
        st.markdown('<h2 class="sub-header">📄 Resume Analysis</h2>', unsafe_allow_html=True)
        
        if not api_key:
            st.markdown('<div class="warning-box">⚠️ Please enter your Google Gemini API Key in the sidebar to proceed.</div>', unsafe_allow_html=True)
            return
        
        # File upload
        uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
        
        if uploaded_file is not None:
            # Extract text from PDF
            with st.spinner("Extracting text from resume..."):
                resume_text = extract_text_from_pdf(uploaded_file)
            
            if resume_text:
                st.success("✅ Resume text extracted successfully!")
                
                # Show extracted text preview
                with st.expander("📄 View Extracted Text (First 500 characters)"):
                    st.text(resume_text[:500] + "..." if len(resume_text) > 500 else resume_text)
                
                # Analysis options
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📋 Generate Summary", use_container_width=True):
                        query = "provide a comprehensive summary highlighting the candidate's qualifications, key experience, skills, projects, and major achievements. Make it concise but informative."
                        
                        with st.spinner("Analyzing resume..."):
                            summary = analyze_resume_with_gemini(resume_text, query, api_key)
                        
                        if summary:
                            st.markdown('<div class="result-box">', unsafe_allow_html=True)
                            st.markdown("### 📋 Resume Summary")
                            st.write(summary)
                            st.markdown('</div>', unsafe_allow_html=True)
                    
                    if st.button("💪 Identify Strengths", use_container_width=True):
                        query = "identify the key strengths, competitive advantages, and standout qualifications that make this candidate attractive to employers. Focus on what makes them unique."
                        
                        with st.spinner("Identifying strengths..."):
                            strengths = analyze_resume_with_gemini(resume_text, query, api_key)
                        
                        if strengths:
                            st.markdown('<div class="result-box">', unsafe_allow_html=True)
                            st.markdown("### 💪 Key Strengths")
                            st.write(strengths)
                            st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    if st.button("⚠️ Identify Weaknesses", use_container_width=True):
                        query = "identify potential weaknesses, gaps, or areas for improvement in this resume. Provide constructive feedback and specific suggestions for enhancement."
                        
                        with st.spinner("Identifying areas for improvement..."):
                            weaknesses = analyze_resume_with_gemini(resume_text, query, api_key)
                        
                        if weaknesses:
                            st.markdown('<div class="result-box">', unsafe_allow_html=True)
                            st.markdown("### ⚠️ Areas for Improvement")
                            st.write(weaknesses)
                            st.markdown('</div>', unsafe_allow_html=True)
                    
                    if st.button("🎯 Job Title Suggestions", use_container_width=True):
                        query = "suggest the most suitable job titles and career positions that align with the candidate's profile. Based on their qualifications, experience, and skills, what roles would be the best fit?"
                        
                        with st.spinner("Generating job suggestions..."):
                            suggestions = analyze_resume_with_gemini(resume_text, query, api_key)
                        
                        if suggestions:
                            st.markdown('<div class="result-box">', unsafe_allow_html=True)
                            st.markdown("### 🎯 Recommended Job Titles")
                            st.write(suggestions)
                            st.markdown('</div>', unsafe_allow_html=True)
                
                # Custom query section
                st.markdown("---")
                st.markdown("### 💬 Ask Custom Questions")
                custom_query = st.text_area("Ask any specific question about the resume:")
                
                if st.button("Get Answer") and custom_query:
                    with st.spinner("Processing your question..."):
                        custom_response = analyze_resume_with_gemini(resume_text, custom_query, api_key)
                    
                    if custom_response:
                        st.markdown('<div class="result-box">', unsafe_allow_html=True)
                        st.markdown("### 💬 Response")
                        st.write(custom_response)
                        st.markdown('</div>', unsafe_allow_html=True)
    
    # AI Job Matching Tab
    elif selected == "🚀 AI Job Matching":
        st.markdown('<h2 class="sub-header">🚀 Resume-to-Job Matching Score</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <h4>🎯 Semantic AI Job Matching</h4>
        <p>Advanced AI analysis that goes beyond keyword matching. Our system understands context and matches related skills 
        (e.g., Pandas ≈ Data Wrangling) to give you accurate job compatibility scores.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not api_key:
            st.markdown('<div class="warning-box">⚠️ Please enter your Google Gemini API Key in the sidebar to proceed.</div>', unsafe_allow_html=True)
        else:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### 📄 Upload Your Resume")
                uploaded_resume = st.file_uploader("Choose your resume (PDF)", type="pdf", key="job_match_resume")
                
            with col2:
                st.markdown("#### 📋 Job Description")
                job_description = st.text_area(
                    "Paste the job description here:", 
                    height=200,
                    placeholder="Paste the complete job description from LinkedIn or company website..."
                )
            
            if uploaded_resume and job_description and st.button("🔍 Analyze Job Match", use_container_width=True):
                with st.spinner("Analyzing resume-job compatibility..."):
                    resume_text = extract_text_from_pdf(uploaded_resume)
                    if resume_text:
                        match_analysis = get_resume_job_match_score(resume_text, job_description, api_key)
                        
                        if match_analysis:
                            st.markdown('<div class="success-box">', unsafe_allow_html=True)
                            st.markdown("### 🎯 Job Match Analysis Results")
                            st.write(match_analysis)
                            st.markdown('</div>', unsafe_allow_html=True)
    
    # Resume Tailoring Tab
    elif selected == "🎨 Resume Tailoring":
        st.markdown('<h2 class="sub-header">🎨 AI Resume Tailoring for Each Job</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <h4>✨ Job-Specific Resume Optimization</h4>
        <p>Automatically customize your resume content for each job application. Our AI rewrites your professional summary, 
        optimizes skills sections, and enhances project descriptions with job-relevant keywords while maintaining ATS compatibility.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not api_key:
            st.markdown('<div class="warning-box">⚠️ Please enter your Google Gemini API Key in the sidebar to proceed.</div>', unsafe_allow_html=True)
        else:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### 📄 Your Current Resume")
                uploaded_resume_tailor = st.file_uploader("Upload resume to tailor (PDF)", type="pdf", key="tailor_resume")
                
            with col2:
                st.markdown("#### 🎯 Target Job")
                target_job_desc = st.text_area(
                    "Target job description:", 
                    height=200,
                    placeholder="Paste the job description you want to tailor your resume for..."
                )
            
            if uploaded_resume_tailor and target_job_desc and st.button("🎨 Generate Tailored Resume", use_container_width=True):
                with st.spinner("Tailoring your resume for this specific job..."):
                    resume_text = extract_text_from_pdf(uploaded_resume_tailor)
                    if resume_text:
                        tailored_content = generate_tailored_resume(resume_text, target_job_desc, api_key)
                        
                        if tailored_content:
                            st.markdown('<div class="success-box">', unsafe_allow_html=True)
                            st.markdown("### ✨ Your Tailored Resume Content")
                            st.write(tailored_content)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Download option
                            st.download_button(
                                label="📥 Download Tailored Resume Content",
                                data=tailored_content,
                                file_name="tailored_resume_content.txt",
                                mime="text/plain"
                            )
    
    # Skill Gap Analysis Tab
    elif selected == "📚 Skill Gap Analysis":
        st.markdown('<h2 class="sub-header">📚 Skill Gap Analyzer + Learning Path Generator</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <h4>🎓 Personalized Learning Roadmap</h4>
        <p>Identify missing or weak skills for your target jobs and get a customized learning path with courses, 
        certifications, and project recommendations. Turn skill gaps into career opportunities!</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not api_key:
            st.markdown('<div class="warning-box">⚠️ Please enter your Google Gemini API Key in the sidebar to proceed.</div>', unsafe_allow_html=True)
        else:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### 📄 Current Resume")
                uploaded_resume_skills = st.file_uploader("Upload your resume (PDF)", type="pdf", key="skills_resume")
                
            with col2:
                st.markdown("#### 🎯 Dream Job Description")
                dream_job_desc = st.text_area(
                    "Target job requirements:", 
                    height=200,
                    placeholder="Paste job description to identify skill gaps and create learning path..."
                )
            
            if uploaded_resume_skills and dream_job_desc and st.button("📊 Analyze Skill Gaps", use_container_width=True):
                with st.spinner("Analyzing skill gaps and creating your personalized learning path..."):
                    resume_text = extract_text_from_pdf(uploaded_resume_skills)
                    if resume_text:
                        skill_analysis = generate_skill_gap_analysis(resume_text, dream_job_desc, api_key)
                        
                        if skill_analysis:
                            st.markdown('<div class="success-box">', unsafe_allow_html=True)
                            st.markdown("### 📈 Your Personalized Learning Roadmap")
                            st.write(skill_analysis)
                            st.markdown('</div>', unsafe_allow_html=True)
    
    # Interview Prep Tab
    elif selected == "🎯 Interview Prep":
        st.markdown('<h2 class="sub-header">🎯 AI Interview Question Generator</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <h4>🎪 Job-Specific Interview Preparation</h4>
        <p>Generate technical and behavioral interview questions based on your resume and target job. 
        Get STAR method response frameworks and model answers tailored to your experience.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not api_key:
            st.markdown('<div class="warning-box">⚠️ Please enter your Google Gemini API Key in the sidebar to proceed.</div>', unsafe_allow_html=True)
        else:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### 📄 Your Resume")
                uploaded_resume_interview = st.file_uploader("Upload resume (PDF)", type="pdf", key="interview_resume")
                
            with col2:
                st.markdown("#### 💼 Interview Job Description")
                interview_job_desc = st.text_area(
                    "Job you're interviewing for:", 
                    height=200,
                    placeholder="Paste the job description for the role you're interviewing for..."
                )
            
            if uploaded_resume_interview and interview_job_desc and st.button("🎯 Generate Interview Questions", use_container_width=True):
                with st.spinner("Creating personalized interview questions based on your profile..."):
                    resume_text = extract_text_from_pdf(uploaded_resume_interview)
                    if resume_text:
                        interview_questions = generate_interview_questions(resume_text, interview_job_desc, api_key)
                        
                        if interview_questions:
                            st.markdown('<div class="success-box">', unsafe_allow_html=True)
                            st.markdown("### 🎪 Your Personalized Interview Preparation")
                            st.write(interview_questions)
                            st.markdown('</div>', unsafe_allow_html=True)
    
    # ATS Checker Tab
    elif selected == "🔍 ATS Checker":
        st.markdown('<h2 class="sub-header">🔍 ATS Compatibility Checker</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <h4>🤖 Beat the Applicant Tracking System</h4>
        <p>Check your resume against ATS rules including keyword density, formatting issues, and section naming. 
        Get specific recommendations to optimize your resume for automated screening systems.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not api_key:
            st.markdown('<div class="warning-box">⚠️ Please enter your Google Gemini API Key in the sidebar to proceed.</div>', unsafe_allow_html=True)
        else:
            st.markdown("#### 📄 Upload Resume for ATS Analysis")
            uploaded_resume_ats = st.file_uploader("Choose your resume (PDF)", type="pdf", key="ats_resume")
            
            if uploaded_resume_ats and st.button("🔍 Run ATS Compatibility Check", use_container_width=True):
                with st.spinner("Analyzing ATS compatibility and optimization opportunities..."):
                    resume_text = extract_text_from_pdf(uploaded_resume_ats)
                    if resume_text:
                        ats_analysis = check_ats_compatibility(resume_text, api_key)
                        
                        if ats_analysis:
                            st.markdown('<div class="success-box">', unsafe_allow_html=True)
                            st.markdown("### 🤖 ATS Compatibility Report")
                            st.write(ats_analysis)
                            st.markdown('</div>', unsafe_allow_html=True)
    
    # Career Paths Tab
    elif selected == "📈 Career Paths":
        st.markdown('<h2 class="sub-header">📈 Career Role Recommendation Engine</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <h4>🚀 Discover Your Career Possibilities</h4>
        <p>Get AI-powered suggestions for alternative career paths based on your skills and experience. 
        Explore lateral moves, growth opportunities, and emerging roles that match your profile.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not api_key:
            st.markdown('<div class="warning-box">⚠️ Please enter your Google Gemini API Key in the sidebar to proceed.</div>', unsafe_allow_html=True)
        else:
            st.markdown("#### 📄 Upload Resume for Career Analysis")
            uploaded_resume_career = st.file_uploader("Choose your resume (PDF)", type="pdf", key="career_resume")
            
            if uploaded_resume_career and st.button("📈 Explore Career Paths", use_container_width=True):
                with st.spinner("Analyzing your profile and discovering career opportunities..."):
                    resume_text = extract_text_from_pdf(uploaded_resume_career)
                    if resume_text:
                        career_recommendations = generate_career_recommendations(resume_text, api_key)
                        
                        if career_recommendations:
                            st.markdown('<div class="success-box">', unsafe_allow_html=True)
                            st.markdown("### 🚀 Your Career Roadmap & Opportunities")
                            st.write(career_recommendations)
                            st.markdown('</div>', unsafe_allow_html=True)
    
    # LinkedIn Scraper Tab
    elif selected == "LinkedIn Scraper":
        st.markdown('<h2 class="sub-header">🔗 LinkedIn Job Scraper</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-box">
        <p>🚀 <strong>LinkedIn Job Scraper</strong> - Automatically extract job listings from LinkedIn based on your search criteria.</p>
        <p>📊 <strong>Get comprehensive job data</strong> including company names, job titles, locations, and URLs.</p>
        <p>💾 <strong>Export functionality</strong> - Download your results as CSV files for further analysis.</p>
        </div>
        
        <div class="warning-box">
        ⚠️ <strong>Important:</strong> LinkedIn may limit automated access. Use responsibly and consider their terms of service.
        </div>
        """, unsafe_allow_html=True)
        
        # Input fields
        col1, col2, col3 = st.columns(3)
        
        with col1:
            job_title = st.text_input("🔍 Job Title", placeholder="e.g., Data Scientist")
        
        with col2:
            location = st.text_input("📍 Location (Optional)", placeholder="e.g., New York, NY")
        
        with col3:
            num_jobs = st.number_input("📊 Number of Jobs", min_value=5, max_value=20, value=10)
        
        if st.button("🚀 Scrape LinkedIn Jobs", use_container_width=True):
            if job_title:
                with st.spinner("Scraping LinkedIn jobs... This may take a few minutes."):
                    jobs_data = scrape_linkedin_jobs(job_title, location, num_jobs)
                
                if jobs_data:
                    st.success(f"✅ Successfully scraped {len(jobs_data)} jobs!")
                    
                    # Display results in a dataframe
                    df = pd.DataFrame(jobs_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Download option
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Jobs Data as CSV",
                        data=csv,
                        file_name=f"linkedin_jobs_{job_title.replace(' ', '_')}.csv",
                        mime="text/csv"
                    )
                    
                    # Display individual job cards
                    st.markdown("### 📋 Job Details")
                    for i, job in enumerate(jobs_data):
                        with st.expander(f"🏢 {job['Title']} at {job['Company']}"):
                            st.markdown(f"**📍 Location:** {job['Location']}")
                            st.markdown(f"**🔗 URL:** [View Job]({job['URL']})")
                            st.markdown("**📝 Description:**")
                            st.write(job['Description'])
                else:
                    st.error("❌ Failed to scrape jobs. LinkedIn may be blocking automated requests or there might be connection issues.")
            else:
                st.warning("⚠️ Please enter a job title to search for.")
    
    # About Tab
    elif selected == "About":
        st.markdown('<h2 class="sub-header">ℹ️ About This Application</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <p>🤖 <strong>AI Resume Analyzer & LinkedIn Scraper</strong></p>
        <p>An advanced AI application that uses Google's Gemini AI for comprehensive resume analysis 
        and Selenium for automated LinkedIn job scraping.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🚀 Comprehensive AI Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **📄 Core Resume Analysis:**
            - 📋 Comprehensive resume summarization
            - 💪 Strength identification
            - ⚠️ Weakness analysis with improvement suggestions
            - 🎯 Personalized job title recommendations
            - 💬 Custom question-answering
            
            **🚀 AI Job Matching:**
            - 🎯 Semantic resume-job compatibility scoring
            - 📊 Skill match percentage analysis
            - 🔍 Experience relevance assessment
            - 💡 Missing skills identification
            """)
        
        with col2:
            st.markdown("""
            **🎨 Resume Enhancement:**
            - ✨ Job-specific resume tailoring
            - 🔍 ATS compatibility checker
            - 📝 Professional summary optimization
            - �️ Keyword optimization
            
            **📚 Career Development:**
            - 📊 Skill gap analysis
            - 🎓 Personalized learning paths
            - 📈 Career progression recommendations
            - 🚀 Alternative role suggestions
            """)
        
        with col3:
            st.markdown("""
            **🎯 Interview Preparation:**
            - 🎪 Job-specific interview questions
            - � STAR method response frameworks
            - 💼 Technical & behavioral questions
            - 🎭 Mock interview scenarios
            
            **🔗 Job Intelligence:**
            - 🔍 LinkedIn job scraping
            - 🏢 Company information extraction
            - 📊 Export & tracking capabilities
            - 🌐 Direct application links
            """)
        
        st.markdown("### 🛠️ Technologies Used")
        
        tech_cols = st.columns(4)
        
        technologies = [
            ("🐍 Python", "Core programming language"),
            ("🤖 Gemini AI", "Google's advanced AI model"),
            ("📊 Streamlit", "Web application framework"),
            ("🔍 Selenium", "Web scraping automation"),
            ("📄 PyPDF2", "PDF text extraction"),
            ("🐼 Pandas", "Data manipulation"),
            ("🌐 Chrome Driver", "Browser automation"),
            ("🔐 python-dotenv", "Environment management")
        ]
        
        for i, (tech, desc) in enumerate(technologies):
            with tech_cols[i % 4]:
                st.markdown(f"**{tech}**")
                st.caption(desc)
        
        st.markdown("### 🎯 How It Works")
        
        st.markdown("""
        <div class="feature-box">
        <h4>Resume Analysis Process:</h4>
        <ol>
        <li>📄 <strong>PDF Text Extraction:</strong> Extract text from uploaded resume using PyPDF2</li>
        <li>🤖 <strong>AI Analysis:</strong> Send structured queries to Google Gemini AI</li>
        <li>💡 <strong>Intelligent Insights:</strong> Get professional-level feedback and recommendations</li>
        <li>📊 <strong>Interactive Results:</strong> View results in formatted, easy-to-read sections</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-box">
        <h4>LinkedIn Scraping Process:</h4>
        <ol>
        <li>🔍 <strong>Search Setup:</strong> Configure job search parameters</li>
        <li>🌐 <strong>Web Automation:</strong> Use Selenium to navigate LinkedIn</li>
        <li>📊 <strong>Data Extraction:</strong> Extract job details automatically</li>
        <li>💾 <strong>Data Processing:</strong> Clean and structure job information</li>
        <li>📥 <strong>Export Options:</strong> Download results as CSV</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🔒 Privacy & Security")
        st.markdown("""
        - **Local Processing:** Resume text is processed locally and sent securely to Google Gemini
        - **No Storage:** Your resume data is not stored on any servers
        - **API Security:** All Gemini AI communications are encrypted
        - **Responsible Scraping:** LinkedIn scraping respects rate limits and ToS
        """)
        
        st.markdown("### ⚠️ Important Notes")
        st.info("""
        **LinkedIn Scraping Disclaimer:** This tool is for educational and personal use. 
        Please respect LinkedIn's terms of service and use responsibly. Consider LinkedIn's 
        official API for production applications.
        """)
        
        st.info("""
        **Gemini API Usage:** This application uses Google's Gemini API which may have usage limits. 
        Monitor your usage through the Google AI Studio console.
        """)
        
        st.markdown("---")
        st.markdown("### 🚀 Getting Started")
        st.markdown("""
        1. **Get Gemini API Key:** Visit [Google AI Studio](https://aistudio.google.com/) to get your API key
        2. **Enter API Key:** Use the sidebar to enter your Gemini API key
        3. **Upload Resume:** Upload a PDF version of your resume
        4. **Analyze:** Use the analysis buttons to get AI-powered insights
        5. **Scrape Jobs:** Search for relevant job opportunities on LinkedIn
        """)

if __name__ == "__main__":
    main()
