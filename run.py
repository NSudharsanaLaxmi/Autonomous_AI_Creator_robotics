"""
Application Launcher
Runs uvicorn server on port 8000.
"""

import uvicorn
import os

if __name__ == "__main__":
    print("Starting Autonomous AI Creator server on http://localhost:8000...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
