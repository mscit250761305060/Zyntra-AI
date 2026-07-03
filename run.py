#!/usr/bin/env python
"""Quick start script for the chatbot application with file-based persistence."""
import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def main():
    print("=" * 60)
    print("🤖 Zyntra AI - File-Based Persistence")
    print("=" * 60)
    
    # Check if .env exists
    if not Path(".env").exists():
        print("\n⚠️  .env file not found!")
        print("   Creating from .env.example...")
        if Path(".env.example").exists():
            with open(".env.example", "r") as f:
                content = f.read()
            with open(".env", "w") as f:
                f.write(content)
            print("   ✅ .env created")
        else:
            print("   ❌ .env.example not found")
    
    # Create data directory if it doesn't exist
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    print("\n✅ Data directories ready")
    
    # Check GEMINI_API_KEY
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("\n⚠️  GEMINI_API_KEY not configured!")
        print("   Set it in .env file: GEMINI_API_KEY=your_key")
    
    print("\n📝 Starting application...")
    print("-" * 60)
    print("🌐 API available at: http://localhost:8000")
    print("📚 API Docs at: http://localhost:8000/api/docs")
    print("❤️  Health check: http://localhost:8000/health")
    print("-" * 60)
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        # Try to open browser to API docs
        print("Opening API documentation in browser...")
        webbrowser.open("http://localhost:8000/api/docs")
    except Exception as e:
        print(f"Could not open browser: {e}")
    
    # Run the application
    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "main:app", "--reload"],
            cwd=os.getcwd()
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
