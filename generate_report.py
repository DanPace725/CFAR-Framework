#!/usr/bin/env python3
"""
CFAR Framework Report Generator Launcher

Quick launcher for generating comprehensive simulation reports
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Launch the report generator"""
    
    if len(sys.argv) < 2:
        print("🎯 CFAR Framework Report Generator")
        print("Usage: python generate_report.py <results_file.json> [options]")
        print()
        print("Options:")
        print("  --html    Generate HTML report (default)")
        print("  --json    Generate JSON analysis summary")
        print("  --csv     Generate CSV data export")
        print("  --all     Generate all formats")
        print()
        print("Example:")
        print("  python generate_report.py engine/results.json --all")
        return
    
    # Pass all arguments to the report generator
    args = ["python", "examples/report_generator.py"] + sys.argv[1:]
    
    try:
        result = subprocess.run(args, cwd=Path.cwd())
        if result.returncode == 0:
            print("\n✅ Report generation completed successfully!")
        else:
            print("\n❌ Report generation failed.")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure you have installed the requirements:")
        print("   pip install -r engine/requirements.txt")

if __name__ == "__main__":
    main()
