import sys
import os

# Add the project root to sys.path so we can import 'app'
# This is critical for Vercel Serverless Functions to find the 'app' folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
