"""
Digital Risk Shield - Server Launcher
Runs the complete platform backend and serves the frontend dashboard at http://localhost:8000
"""

import uvicorn
import os
import sys

# Ensure root workspace is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

if __name__ == "__main__":
    print("=" * 70)
    print("  DIGITAL RISK SHIELD - BRAND IMPERSONATION & RISK DETECTION")
    print("=" * 70)
    print("  * Dashboard UI:      http://localhost:8000")
    print("  * Interactive API:   http://localhost:8000/docs")
    print("  * OpenAPI Schema:    http://localhost:8000/openapi.json")
    print("=" * 70)
    print("Starting Uvicorn server...")
    
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
