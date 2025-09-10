#!/usr/bin/env python3
"""
CFAR Framework API Server Launcher

Quick launcher for the FastAPI backend server
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch the FastAPI server"""
    
    # Change to project root
    project_root = Path(__file__).parent
    
    # Launch FastAPI server
    try:
        print("🚀 Starting CFAR Framework API Server...")
        print("📍 API will be available at: http://localhost:8000")
        print("📖 API documentation at: http://localhost:8000/docs")
        print("⏹️  Press Ctrl+C to stop the server")
        print()
        
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "ui.api.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ], cwd=project_root)
        
    except KeyboardInterrupt:
        print("\n👋 API server stopped by user")
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        print("\n💡 Make sure you have installed the requirements:")
        print("   pip install -r engine/requirements.txt")

if __name__ == "__main__":
    main()
