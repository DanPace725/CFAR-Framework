#!/usr/bin/env python3
"""
CFAR Framework Dashboard Launcher

Quick launcher for the Streamlit dashboard
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch the Streamlit dashboard"""
    
    # Change to project root
    project_root = Path(__file__).parent
    
    # Launch Streamlit app
    try:
        print("🚀 Starting CFAR Framework Dashboard...")
        print("📍 Dashboard will open in your browser at: http://localhost:8501")
        print("⏹️  Press Ctrl+C to stop the dashboard")
        print()
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(project_root / "ui" / "streamlit_app.py"),
            "--server.port", "8501",
            "--server.headless", "false"
        ], cwd=project_root)
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        print("\n💡 Make sure you have installed the requirements:")
        print("   pip install -r engine/requirements.txt")

if __name__ == "__main__":
    main()
