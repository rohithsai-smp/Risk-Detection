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
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    # Enable reload by default in local dev, disable if hosted on cloud or RELOAD=0
    reload = os.environ.get("RELOAD", "false" if os.environ.get("PORT") else "true").lower() in ("true", "1")

    print("=" * 70)
    print("  DIGITAL RISK SHIELD - BRAND IMPERSONATION & RISK DETECTION")
    print("=" * 70)
    print(f"  * Dashboard UI:      http://localhost:{port}")
    print(f"  * Interactive API:   http://localhost:{port}/docs")
    print(f"  * OpenAPI Schema:    http://localhost:{port}/openapi.json")
    print(f"  * Health Endpoint:   http://localhost:{port}/api/health")
    print("=" * 70)
    print(f"Starting Uvicorn server on {host}:{port} (reload={reload})...")
    
    uvicorn.run("backend.app.main:app", host=host, port=port, reload=reload)
