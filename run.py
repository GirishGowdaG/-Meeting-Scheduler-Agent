#!/usr/bin/env python3
"""
SmartMeet Quick Run Script
Simple script to start both backend and frontend
"""
import subprocess
import sys
import os
from pathlib import Path
import time

def main():
    print("=" * 60)
    print("  SmartMeet - Starting Services")
    print("=" * 60)
    print()
    
    # Check if .env exists
    if not Path("backend/.env").exists():
        print("⚠️  ERROR: backend/.env file not found!")
        print()
        print("Please run setup first:")
        print("  python setup_and_run.py")
        print()
        print("Or manually:")
        print("  1. Copy backend/.env.example to backend/.env")
        print("  2. Add your Google OAuth and Anthropic API credentials")
        print("  3. Run: cd backend && python scripts/generate_keys.py")
        sys.exit(1)
    
    print("Starting backend on http://localhost:8000")
    print("Starting frontend on http://localhost:3000")
    print()
    print("Press Ctrl+C to stop all services")
    print()
    
    # Start backend
    backend_cmd = [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"]
    backend_process = subprocess.Popen(
        backend_cmd,
        cwd="backend",
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )
    
    # Wait a bit for backend to start
    time.sleep(2)
    
    # Start frontend
    frontend_cmd = ["npm", "run", "dev"]
    frontend_process = subprocess.Popen(
        frontend_cmd,
        cwd="frontend",
        shell=True,
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )
    
    print("✓ Services started!")
    print()
    print("  Frontend: http://localhost:3000")
    print("  Backend:  http://localhost:8000")
    print("  API Docs: http://localhost:8000/docs")
    print()
    print("Close the console windows to stop services")
    print()
    
    try:
        # Keep script running
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nStopping services...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✓ Services stopped")

if __name__ == "__main__":
    main()
