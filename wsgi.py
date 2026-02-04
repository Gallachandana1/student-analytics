import sys
import os

# Base directory
base_dir = os.path.dirname(os.path.abspath(__file__))
# Backend directory
backend_dir = os.path.join(base_dir, 'backend')

# Add backend to path so that 'from app import app' works 
# and internal backend imports work as well.
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import the Flask app instance from backend/app.py
from app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
