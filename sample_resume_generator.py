# Sample resume for testing the application
# This file demonstrates how to create test data

import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

def create_sample_resume():
    """Create a sample PDF resume for testing"""
    
    # Create a PDF in memory
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Add content to the PDF
    y_position = height - 50
    
    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y_position, "John Doe")
    y_position -= 20
    
    p.setFont("Helvetica", 12)
    p.drawString(50, y_position, "Email: john.doe@email.com | Phone: (555) 123-4567")
    y_position -= 15
    p.drawString(50, y_position, "LinkedIn: linkedin.com/in/johndoe | Location: New York, NY")
    y_position -= 30
    
    # Professional Summary
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y_position, "Professional Summary")
    y_position -= 20
    
    p.setFont("Helvetica", 11)
    summary_text = [
        "Experienced Data Scientist with 5+ years in machine learning and AI.",
        "Proven track record in developing predictive models and data-driven solutions.",
        "Expert in Python, SQL, and cloud technologies with strong business acumen."
    ]
    
    for line in summary_text:
        p.drawString(50, y_position, line)
        y_position -= 15
    
    y_position -= 15
    
    # Experience
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y_position, "Work Experience")
    y_position -= 20
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y_position, "Senior Data Scientist - Tech Company Inc.")
    y_position -= 15
    p.setFont("Helvetica", 11)
    p.drawString(50, y_position, "January 2021 - Present")
    y_position -= 15
    
    experience_points = [
        "• Developed machine learning models that improved prediction accuracy by 25%",
        "• Led cross-functional team of 6 engineers in AI product development",
        "• Implemented automated data pipelines processing 10M+ records daily",
        "• Collaborated with stakeholders to translate business requirements into technical solutions"
    ]
    
    for point in experience_points:
        p.drawString(50, y_position, point)
        y_position -= 12
    
    y_position -= 10
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y_position, "Data Analyst - Analytics Corp")
    y_position -= 15
    p.setFont("Helvetica", 11)
    p.drawString(50, y_position, "June 2019 - December 2020")
    y_position -= 15
    
    analyst_points = [
        "• Created interactive dashboards and reports for executive leadership",
        "• Performed statistical analysis on customer behavior data",
        "• Optimized SQL queries reducing report generation time by 40%"
    ]
    
    for point in analyst_points:
        p.drawString(50, y_position, point)
        y_position -= 12
    
    y_position -= 15
    
    # Skills
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y_position, "Technical Skills")
    y_position -= 20
    
    p.setFont("Helvetica", 11)
    skills_text = [
        "Programming: Python, R, SQL, JavaScript, Java",
        "Machine Learning: Scikit-learn, TensorFlow, PyTorch, Keras",
        "Data Tools: Pandas, NumPy, Matplotlib, Seaborn, Tableau, Power BI",
        "Cloud Platforms: AWS, Google Cloud Platform, Azure",
        "Databases: PostgreSQL, MySQL, MongoDB, Redis"
    ]
    
    for skill_line in skills_text:
        p.drawString(50, y_position, skill_line)
        y_position -= 12
    
    y_position -= 15
    
    # Education
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y_position, "Education")
    y_position -= 20
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y_position, "Master of Science in Data Science")
    y_position -= 15
    p.setFont("Helvetica", 11)
    p.drawString(50, y_position, "University of Technology - 2019")
    y_position -= 15
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y_position, "Bachelor of Science in Computer Science")
    y_position -= 15
    p.setFont("Helvetica", 11)
    p.drawString(50, y_position, "State University - 2017")
    
    # Save the PDF
    p.save()
    buffer.seek(0)
    
    return buffer

if __name__ == "__main__":
    # This would be used to generate a sample resume file
    pass
