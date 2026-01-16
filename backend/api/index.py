"""
Vercel serverless function wrapper for FastAPI app
"""
import sys
import os

# Add parent directory to path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangum import Mangum
from app.main import app

# Wrap FastAPI app with Mangum for Vercel/Lambda compatibility
handler = Mangum(app, lifespan="off")  # Disable lifespan events for serverless
