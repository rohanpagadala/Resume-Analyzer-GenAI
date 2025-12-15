# 🤖 AI Resume Analyzer & LinkedIn Scraper

An advanced AI application that leverages Google's Gemini AI for comprehensive resume analysis and automated LinkedIn job scraping using Selenium web automation.

## Features

### 📄 Resume Analysis
- **Comprehensive Summarization**: Get detailed resume summaries highlighting qualifications, experience, skills, and achievements
- **Strength Identification**: Discover competitive advantages and standout qualifications
- **Weakness Analysis**: Identify areas for improvement with actionable suggestions  
- **Job Title Recommendations**: Get personalized job title suggestions based on your profile
- **Custom Q&A**: Ask specific questions about your resume and get AI-powered answers

### LinkedIn Job Scraping
- **Automated Job Search**: Search for jobs by title and location
- **Comprehensive Data Extraction**: Get company names, job titles, locations, URLs, and descriptions
- **Export Functionality**: Download job data as CSV files
- **Interactive Display**: Browse jobs in an easy-to-read format

## Technology Stack

- **Python** - Core programming language
- **Streamlit** - Web application framework
- **Google Gemini AI** - Advanced AI model for analysis
- **Selenium** - Web scraping automation
- **PyPDF2** - PDF text extraction
- **Pandas** - Data manipulation and export

## Quick Start

### Option 1: Easy Setup (Recommended)
```bash
python run_app.py
```
This will automatically:
- Install all required packages
- Check your API key setup
- Start the application

### Option 2: Manual Setup
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API key** (Already configured!)
   - The `.env` file already contains your Gemini API key
   - If you need a new key, visit [Google AI Studio](https://aistudio.google.com/)

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access the app**
   Open your browser and go to `http://localhost:8501`

## 🔧 Configuration

### Google Gemini API Key
You'll need a Google Gemini API key to use the resume analysis features. You can:
- Enter it directly in the sidebar when using the app
- Set it in the `.env` file as `GEMINI_API_KEY=your_key_here`
- Set it as an environment variable

### Chrome Driver
The LinkedIn scraper uses Chrome WebDriver, which is automatically managed by `webdriver-manager`. Make sure you have Chrome browser installed on your system.

## Usage Guide

### Resume Analysis
1. **Upload PDF**: Select your resume file (PDF format only)
2. **Enter API Key**: Provide your OpenAI API key in the sidebar
3. **Choose Analysis Type**:
   - **Summary**: Get a comprehensive overview of your resume
   - **Strengths**: Identify your competitive advantages
   - **Weaknesses**: Find areas for improvement
   - **Job Suggestions**: Get recommended job titles
   - **Custom Questions**: Ask specific questions about your resume

### LinkedIn Job Scraping
1. **Enter Job Details**:
   - Job Title (required): e.g., "Data Scientist"
   - Location (optional): e.g., "New York, NY"
   - Number of Jobs: Choose how many jobs to scrape (5-50)
2. **Start Scraping**: Click "Scrape LinkedIn Jobs"
3. **View Results**: Browse jobs in the interactive table
4. **Export Data**: Download results as CSV for further analysis

## How It Works

### Resume Analysis Pipeline
1. **PDF Processing**: Extract text from uploaded PDF using PyPDF2
2. **Text Chunking**: Split content into manageable chunks using LangChain
3. **Vectorization**: Convert text to embeddings using OpenAI's embedding model
4. **Vector Storage**: Store embeddings in FAISS for efficient similarity search
5. **Query Processing**: Match user queries with relevant resume sections
6. **AI Analysis**: Generate insights using GPT-3.5 Turbo model

### LinkedIn Scraping Process
1. **Search Configuration**: Set up job search parameters
2. **Browser Automation**: Launch headless Chrome browser with Selenium
3. **Data Extraction**: Navigate LinkedIn and extract job information
4. **Data Processing**: Clean and structure the scraped data
5. **Result Display**: Present data in user-friendly format with export options

## Key Benefits

- **Time-Saving**: Automated analysis and job searching
- **AI-Powered Insights**: Get professional-level resume feedback
- **Comprehensive Data**: Extract detailed job information efficiently
- **Export Options**: Save and analyze data offline
- **User-Friendly**: Intuitive interface suitable for all skill levels

## Privacy & Security

- **Local Processing**: Resume analysis happens locally with secure API calls
- **No Data Storage**: Your resume data is not stored on servers
- **Secure Connections**: All API communications are encrypted
- **Optional Headless Mode**: LinkedIn scraping can run in background

## Important Notes

### LinkedIn Scraping Disclaimer
- This tool is for educational and personal use only
- Respect LinkedIn's terms of service and rate limits
- Consider LinkedIn's robots.txt and API alternatives for production use
- Be mindful of scraping frequency to avoid IP blocking

### API Usage
- OpenAI API calls incur costs based on usage
- Monitor your API usage through the OpenAI dashboard
- The application uses GPT-3.5 Turbo for cost-effectiveness

## Troubleshooting

### Common Issues

**Import Errors**
- Ensure all packages are installed: `pip install -r requirements.txt`
- Check Python version compatibility (3.8+)

**Chrome Driver Issues**
- Make sure Chrome browser is installed
- Check if webdriver-manager can access the internet
- Try running with different Chrome options if needed

**OpenAI API Errors**
- Verify your API key is correct and has credits
- Check if you have access to the required models
- Monitor rate limits and usage quotas

**LinkedIn Scraping Issues**
- LinkedIn may block frequent requests
- Try using different search terms or reducing request frequency
- Consider using VPN if IP is blocked

## Future Enhancements

I'd like to add several features to make this application even more powerful. Here are some ideas:

### Potential Additions
- **Multi-format Support**: Support for Word documents, plain text files
- **Batch Processing**: Analyze multiple resumes simultaneously  
- **Resume Templates**: Generate improved resume versions
- **Skill Gap Analysis**: Compare resume with job requirements
- **Industry-Specific Analysis**: Tailored feedback for different sectors
- **ATS Optimization**: Check resume compatibility with ATS systems
- **Interview Preparation**: Generate potential interview questions
- **Salary Insights**: Integration with salary data APIs
- **Job Alert System**: Automated job matching and notifications
- **Resume Version Control**: Track resume improvements over time

## Contributing

Contributions are welcome! Feel free to:
- Report bugs or issues
- Suggest new features  
- Submit pull requests
- Improve documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Review the GitHub issues for similar problems
3. Create a new issue with detailed information about the problem

## Acknowledgments

- OpenAI for providing powerful language models
- LangChain community for excellent RAG framework
- Streamlit team for the amazing web app framework
- Selenium contributors for web automation capabilities

---

**Happy Job Hunting! 🎯**
# Resume-Analyzer-GenAI
