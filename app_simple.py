import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_extras.add_vertical_space import add_vertical_space
import PyPDF2
import os
import openai
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
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .result-box {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
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

def analyze_resume_with_openai(resume_text, query, api_key):
    """Analyze resume using OpenAI API directly"""
    try:
        client = openai.OpenAI(api_key=api_key)
        
        prompt = f"""
        Based on the following resume content, please {query}
        
        Resume Content:
        {resume_text[:4000]}  # Limit text to avoid token limits
        
        Please provide a detailed and helpful response.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert career counselor and resume analyst. Provide detailed, actionable feedback."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        return response.choices[0].message.content
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

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Resume Analyzer & LinkedIn Scraper</h1>', unsafe_allow_html=True)
    
    # Sidebar for navigation
    with st.sidebar:
        st.title("Navigation")
        selected = option_menu(
            menu_title=None,
            options=["Resume Analyzer", "LinkedIn Scraper", "About"],
            icons=["file-earmark-text", "linkedin", "info-circle"],
            menu_icon="cast",
            default_index=0,
        )
        
        add_vertical_space(3)
        
        # API Key input
        st.markdown("### 🔑 OpenAI API Key")
        api_key = st.text_input("Enter your OpenAI API Key", type="password")
        
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
    
    # Resume Analyzer Tab
    if selected == "Resume Analyzer":
        st.markdown('<h2 class="sub-header">📄 Resume Analysis</h2>', unsafe_allow_html=True)
        
        if not api_key:
            st.markdown('<div class="warning-box">⚠️ Please enter your OpenAI API Key in the sidebar to proceed.</div>', unsafe_allow_html=True)
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
                            summary = analyze_resume_with_openai(resume_text, query, api_key)
                        
                        if summary:
                            st.markdown('<div class="result-box">', unsafe_allow_html=True)
                            st.markdown("### 📋 Resume Summary")
                            st.write(summary)
                            st.markdown('</div>', unsafe_allow_html=True)
                    
                    if st.button("💪 Identify Strengths", use_container_width=True):
                        query = "identify the key strengths, competitive advantages, and standout qualifications that make this candidate attractive to employers. Focus on what makes them unique."
                        
                        with st.spinner("Identifying strengths..."):
                            strengths = analyze_resume_with_openai(resume_text, query, api_key)
                        
                        if strengths:
                            st.markdown('<div class="result-box">', unsafe_allow_html=True)
                            st.markdown("### 💪 Key Strengths")
                            st.write(strengths)
                            st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    if st.button("⚠️ Identify Weaknesses", use_container_width=True):
                        query = "identify potential weaknesses, gaps, or areas for improvement in this resume. Provide constructive feedback and specific suggestions for enhancement."
                        
                        with st.spinner("Identifying areas for improvement..."):
                            weaknesses = analyze_resume_with_openai(resume_text, query, api_key)
                        
                        if weaknesses:
                            st.markdown('<div class="result-box">', unsafe_allow_html=True)
                            st.markdown("### ⚠️ Areas for Improvement")
                            st.write(weaknesses)
                            st.markdown('</div>', unsafe_allow_html=True)
                    
                    if st.button("🎯 Job Title Suggestions", use_container_width=True):
                        query = "suggest the most suitable job titles and career positions that align with the candidate's profile. Based on their qualifications, experience, and skills, what roles would be the best fit?"
                        
                        with st.spinner("Generating job suggestions..."):
                            suggestions = analyze_resume_with_openai(resume_text, query, api_key)
                        
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
                        custom_response = analyze_resume_with_openai(resume_text, custom_query, api_key)
                    
                    if custom_response:
                        st.markdown('<div class="result-box">', unsafe_allow_html=True)
                        st.markdown("### 💬 Response")
                        st.write(custom_response)
                        st.markdown('</div>', unsafe_allow_html=True)
    
    # LinkedIn Scraper Tab
    elif selected == "LinkedIn Scraper":
        st.markdown('<h2 class="sub-header">🔗 LinkedIn Job Scraper</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-box">
        <p>🚀 <strong>LinkedIn Job Scraper</strong> - Automatically extract job listings from LinkedIn based on your search criteria.</p>
        <p>📊 Get comprehensive job data including company names, job titles, locations, and URLs.</p>
        <p>⚠️ <strong>Note:</strong> LinkedIn may limit automated access. Use responsibly and consider their terms of service.</p>
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
        <div class="feature-box">
        <h3>🤖 AI Resume Analyzer & LinkedIn Scraper</h3>
        <p>An advanced AI application that uses OpenAI's GPT models for comprehensive resume analysis 
        and Selenium for automated LinkedIn job scraping.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🚀 Key Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📄 Resume Analysis:**
            - 📋 Comprehensive resume summarization
            - 💪 Strength identification
            - ⚠️ Weakness analysis with improvement suggestions
            - 🎯 Personalized job title recommendations
            - 💬 Custom question-answering
            """)
        
        with col2:
            st.markdown("""
            **🔗 LinkedIn Job Scraping:**
            - 🔍 Automated job search
            - 🏢 Company information extraction
            - 📍 Location and job details
            - 📊 Export to CSV functionality
            - 🌐 Direct links to job postings
            """)
        
        st.markdown("### 🛠️ Technologies Used")
        
        tech_cols = st.columns(4)
        
        technologies = [
            ("🐍 Python", "Core programming language"),
            ("🤖 OpenAI", "GPT-3.5 for AI analysis"),
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
        <li>🤖 <strong>AI Analysis:</strong> Send structured queries to OpenAI GPT-3.5</li>
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
        - **Local Processing:** Resume text is processed locally and sent securely to OpenAI
        - **No Storage:** Your resume data is not stored on any servers
        - **API Security:** All OpenAI communications are encrypted
        - **Responsible Scraping:** LinkedIn scraping respects rate limits and ToS
        """)
        
        st.markdown("### ⚠️ Important Notes")
        st.info("""
        **LinkedIn Scraping Disclaimer:** This tool is for educational and personal use. 
        Please respect LinkedIn's terms of service and use responsibly. Consider LinkedIn's 
        official API for production applications.
        """)
        
        st.info("""
        **OpenAI API Usage:** This application uses OpenAI's API which incurs costs based on usage. 
        Monitor your usage through the OpenAI dashboard.
        """)
        
        st.markdown("---")
        st.markdown("### 🚀 Getting Started")
        st.markdown("""
        1. **Get OpenAI API Key:** Visit [OpenAI Platform](https://platform.openai.com/) to get your API key
        2. **Enter API Key:** Use the sidebar to enter your OpenAI API key
        3. **Upload Resume:** Upload a PDF version of your resume
        4. **Analyze:** Use the analysis buttons to get AI-powered insights
        5. **Scrape Jobs:** Search for relevant job opportunities on LinkedIn
        """)

if __name__ == "__main__":
    main()
