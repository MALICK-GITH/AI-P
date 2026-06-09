import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from app.main import app

print("Starting server on http://127.0.0.1:8000")
uvicorn.run(app, host="0.0.0.0", port=8000)