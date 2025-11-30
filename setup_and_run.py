#!/usr/bin/env python3
"""
SmartMeet Setup and Run Script
Automates the complete setup and launch process
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def run_command(cmd, cwd=None, shell=True):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, cwd=cwd, shell=shell, check=True, 
                              capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except FileNotFoundError as e:
        return False, str(e)

def check_prerequisites():
    """Check if required tools are installed"""
    print_header("Checking Prerequisites")
    
    # Check Python
    try:
        python_version = sys.version.split()[0]
        print(f"✓ Python {python_version} found")
        if sys.version_info < (3, 11):
            print("⚠️  Warning: Python 3.11+ recommended")
    except:
        print("✗ Python not found")
        return False
    
    # Check Node.js
    success, output = run_command("node --version", shell=True)
    if success:
        print(f"✓ Node.js {output.strip()} found")
    else:
        print("✗ Node.js not found - please install Node.js 20+")
        return False
    
    # Check npm
    success, output = run_command("npm --version", shell=True)
    if success:
        print(f"✓ npm {output.strip()} found")
    else:
        print("✗ npm not found")
        return False
    
    return True

def setup_backend():
    """Setup backend environment"""
    print_header("Setting Up Backend")
    
    backend_dir = Path("backend")
    venv_dir = backend_dir / ".venv"
    
    # Create virtual environment if it doesn't exist
    if not venv_dir.exists():
        print("Creating virtual environment...")
        success, _ = run_command(f"{sys.executable} -m venv .venv", cwd=backend_dir)
        if not success:
            print("✗ Failed to create virtual environment")
            return False
        print("✓ Virtual environment created")
    else:
        print("✓ Virtual environment already exists")
    
    # Determine pip path
    if platform.system() == "Windows":
        pip_path = venv_dir / "Scripts" / "pip.exe"
        python_path = venv_dir / "Scripts" / "python.exe"
    else:
        pip_path = venv_dir / "bin" / "pip"
        python_path = venv_dir / "bin" / "python"
    
    # Install dependencies
    print("Installing Python dependencies...")
    success, _ = run_command(f"{pip_path} install -q -r requirements.txt", cwd=backend_dir, shell=True)
    if not success:
        print("⚠️  Some dependencies may have failed to install")
    else:
        print("✓ Python dependencies installed")
    
    # Check for .env file
    env_file = backend_dir / ".env"
    env_example = backend_dir / ".env.example"
    
    if not env_file.exists():
        print("\n⚠️  Backend .env file not found!")
        print("Creating .env from template...")
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print("✓ Created .env file")
            print("\n⚠️  IMPORTANT: Edit backend/.env with your credentials:")
            print("   - GOOGLE_CLIENT_ID")
            print("   - GOOGLE_CLIENT_SECRET")
            print("   - ANTHROPIC_API_KEY")
            print("   - SECRET_KEY (generate with: python scripts/generate_keys.py)")
            print("   - ENCRYPTION_KEY (generate with: python scripts/generate_keys.py)")
            
            # Generate keys
            print("\nGenerating SECRET_KEY and ENCRYPTION_KEY...")
            success, output = run_command(f"{python_path} scripts/generate_keys.py", cwd=backend_dir, shell=True)
            if success:
                print(output)
    else:
        print("✓ Backend .env file exists")
    
    # Initialize database
    db_file = backend_dir / "smartmeet.db"
    if not db_file.exists():
        print("Initializing database...")
        success, output = run_command(f"{python_path} scripts/init_db.py", cwd=backend_dir, shell=True)
        if success:
            print("✓ Database initialized")
        else:
            print("⚠️  Database initialization may have issues")
    else:
        print("✓ Database already exists")
    
    return True

def setup_frontend():
    """Setup frontend environment"""
    print_header("Setting Up Frontend")
    
    frontend_dir = Path("frontend")
    node_modules = frontend_dir / "node_modules"
    
    # Install dependencies
    if not node_modules.exists():
        print("Installing Node.js dependencies (this may take a few minutes)...")
        success, _ = run_command("npm install", cwd=frontend_dir, shell=True)
        if not success:
            print("✗ Failed to install Node.js dependencies")
            return False
        print("✓ Node.js dependencies installed")
    else:
        print("✓ Node.js dependencies already installed")
    
    # Check for .env.local file
    env_file = frontend_dir / ".env.local"
    env_example = frontend_dir / ".env.example"
    
    if not env_file.exists():
        print("Creating .env.local from template...")
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print("✓ Created .env.local file")
    else:
        print("✓ Frontend .env.local file exists")
    
    return True

def start_services():
    """Start backend and frontend services"""
    print_header("Starting Services")
    
    print("Starting backend and frontend...")
    print("Backend will run on: http://localhost:8000")
    print("Frontend will run on: http://localhost:3000")
    print("\nPress Ctrl+C to stop all services\n")
    
    backend_dir = Path("backend")
    frontend_dir = Path("frontend")
    
    # Determine python path
    if platform.system() == "Windows":
        python_path = backend_dir / ".venv" / "Scripts" / "python.exe"
        uvicorn_path = backend_dir / ".venv" / "Scripts" / "uvicorn.exe"
    else:
        python_path = backend_dir / ".venv" / "bin" / "python"
        uvicorn_path = backend_dir / ".venv" / "bin" / "uvicorn"
    
    try:
        # Start backend
        backend_process = subprocess.Popen(
            [str(uvicorn_path), "main:app", "--reload", "--port", "8000"],
            cwd=backend_dir
        )
        
        # Start frontend
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            shell=True
        )
        
        print("✓ Services started successfully!")
        print("\nOpen http://localhost:3000 in your browser")
        print("\nPress Ctrl+C to stop...\n")
        
        # Wait for processes
        backend_process.wait()
        frontend_process.wait()
        
    except KeyboardInterrupt:
        print("\n\nStopping services...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✓ Services stopped")

def main():
    """Main setup and run function"""
    print_header("SmartMeet Setup & Run")
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n✗ Prerequisites check failed. Please install required tools.")
        sys.exit(1)
    
    # Setup backend
    if not setup_backend():
        print("\n✗ Backend setup failed")
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend():
        print("\n✗ Frontend setup failed")
        sys.exit(1)
    
    print_header("Setup Complete!")
    print("All components are ready.")
    
    # Ask if user wants to start services
    response = input("\nStart services now? (y/n): ").strip().lower()
    if response == 'y':
        start_services()
    else:
        print("\nTo start services later, run:")
        print("  python setup_and_run.py")
        print("\nOr manually:")
        print("  Backend:  cd backend && uvicorn main:app --reload")
        print("  Frontend: cd frontend && npm run dev")

if __name__ == "__main__":
    main()
