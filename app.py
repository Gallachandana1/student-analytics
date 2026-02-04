import sys
import os

# Add the backend directory to sys.path so that internal imports 
# like 'from database import ...' work correctly.
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import the Flask app instance from backend/app.py
from app import app

# This allows 'gunicorn app:app' to work from the root
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
