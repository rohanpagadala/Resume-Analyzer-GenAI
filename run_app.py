#!/usr/bin/env python3
"""
Simple setup and run script for AI Resume Analyzer
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("🔧 Installing required packages...")
    try:
        # Install from requirements.txt
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        # Ensure streamlit components are installed correctly
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit-option-menu", "streamlit-extras"])
        
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has API key"""
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
            if "GEMINI_API_KEY=" in content and "AIzaSy" in content:
                print("✅ API key found in .env file")
                return True
            else:
                print("⚠️ .env file exists but API key not found")
                return False
    else:
        print("⚠️ .env file not found")
        return False

def run_app():
    """Run the Streamlit app"""
    print("🚀 Starting AI Resume Analyzer...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running app: {e}")

def main():
    print("🤖 AI Resume Analyzer - Setup & Run")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ app.py not found. Please run this script from the project directory.")
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements. Please check your Python environment.")
        sys.exit(1)
    
    # Check API key
    if not check_env_file():
        print("\n📝 API Key Setup:")
        print("1. The .env file already contains your Gemini API key")
        print("2. If you need a new key, visit: https://aistudio.google.com/")
        print("3. The app will load the key automatically from .env file")
    
    print("\n" + "=" * 40)
    print("🎉 Setup complete! Starting the application...")
    print("💡 The app will open in your browser at http://localhost:8501")
    print("📝 To stop the app, press Ctrl+C in this terminal")
    print("=" * 40)
    
    # Run the app
    run_app()

if __name__ == "__main__":
    main()
