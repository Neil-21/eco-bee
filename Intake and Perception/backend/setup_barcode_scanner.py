#!/usr/bin/env python3
"""
Setup script for EcoBee Intake & Perception with Pixtral Barcode Scanner
This script helps configure the environment for barcode scanning functionality
"""

import os
import sys
import subprocess
from pathlib import Path

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install some packages")
        return False

def check_api_key():
    """Check if Mistral API key is configured"""
    # First check if .env file exists and load it
    env_file = Path(".env")
    if env_file.exists():
        if DOTENV_AVAILABLE:
            load_dotenv()
            print("✅ Found .env file")
        else:
            print("⚠️  python-dotenv not installed, checking environment variables only...")
    
    api_key = os.getenv('MISTRAL_API_KEY')
    if api_key:
        print("✅ Mistral API key is configured")
        print(f"   API key: {api_key[:8]}...")  # Show first 8 chars for verification
        return True
    else:
        print("⚠️  Mistral API key not found")
        if env_file.exists():
            print("   .env file exists but MISTRAL_API_KEY not found in it")
            print("   Please add: MISTRAL_API_KEY=your_api_key_here to your .env file")
        else:
            print("   Please create a .env file with: MISTRAL_API_KEY=your_api_key_here")
            print("   Or set the environment variable:")
        print("   You can get an API key from: https://console.mistral.ai/")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🧪 Testing imports...")
    required_modules = [
        ('PIL', 'Pillow'),
        ('requests', 'requests'),
        ('json', 'built-in'),
        ('base64', 'built-in'),
        ('io', 'built-in')
    ]
    
    all_good = True
    for module, package in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} ({package})")
        except ImportError:
            print(f"❌ {module} ({package}) - missing")
            all_good = False
    
    return all_good

def test_barcode_scanner():
    """Test barcode scanner initialization"""
    print("\n🔍 Testing barcode scanner...")
    try:
        from barcode_scanner import create_scanner
        scanner = create_scanner()
        print("✅ Barcode scanner initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Barcode scanner failed to initialize: {e}")
        return False

def main():
    """Main setup function"""
    print("🌱 EcoBee Barcode Scanner Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Setup failed: Could not install required packages")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("\n❌ Setup failed: Some required modules are missing")
        sys.exit(1)
    
    # Test barcode scanner
    scanner_ok = test_barcode_scanner()
    
    # Check API key
    api_key_ok = check_api_key()
    
    print("\n" + "=" * 40)
    print("📊 Setup Summary:")
    print(f"   Python: ✅")
    print(f"   Packages: ✅")
    print(f"   Imports: ✅")
    print(f"   Scanner: {'✅' if scanner_ok else '❌'}")
    print(f"   API Key: {'✅' if api_key_ok else '⚠️'}")
    
    if scanner_ok and api_key_ok:
        print("\n🎉 Setup complete! Barcode scanning is ready to use.")
        print("\n🚀 To start the server:")
        print("   python simple_server.py")
    elif scanner_ok:
        print("\n⚠️  Setup partially complete. Set MISTRAL_API_KEY to enable barcode scanning.")
        print("\n🚀 To start the server:")
        print("   python simple_server.py")
    else:
        print("\n❌ Setup incomplete. Please fix the issues above.")

if __name__ == "__main__":
    main()
