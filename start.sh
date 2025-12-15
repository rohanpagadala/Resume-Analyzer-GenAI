#!/bin/bash

# AI Resume Analyzer Startup Script
# This script sets up and runs the AI Resume Analyzer application

echo "🚀 Starting AI Resume Analyzer..."
echo "=================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    echo "Run: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if required packages are installed
echo "🔍 Checking dependencies..."
python -c "
import streamlit
import openai
import selenium
import PyPDF2
print('✅ All core dependencies found!')
" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ] && [ ! -f ".env" ]; then
    echo "⚠️ OpenAI API Key not found in environment or .env file"
    echo "💡 You can:"
    echo "   1. Set environment variable: export OPENAI_API_KEY='your-key'"
    echo "   2. Create .env file with: OPENAI_API_KEY=your-key"
    echo "   3. Enter it in the app sidebar when running"
fi

echo "🌐 Starting Streamlit server..."
echo "📱 The app will open at: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Run the Streamlit app
streamlit run app.py --server.port 8501 --server.address localhost
