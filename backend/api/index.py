"""
Vercel serverless function wrapper for FastAPI app
"""
import sys
import os

# Add parent directory to path so we can import the app
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Set working directory to backend root
os.chdir(backend_dir)

from mangum import Mangum
from app.main import app

# Wrap FastAPI app with Mangum for Vercel/Lambda compatibility
# Disable lifespan events since serverless functions handle initialization differently
handler = Mangum(app, lifespan="off", enable_lifespan=False)
