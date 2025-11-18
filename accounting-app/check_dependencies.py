#!/usr/bin/env python3
"""
Dependency checker for the Personal Accounting App.
Run this script to verify all required dependencies are installed.
"""

import sys

def check_python_version():
    """Check if Python version is 3.6 or higher."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.6+ required.")
        return False
    else:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
        return True

def check_module(module_name, import_name=None, optional=False):
    """Check if a Python module is installed."""
    if import_name is None:
        import_name = module_name

    try:
        __import__(import_name)
        print(f"✓ {module_name} is installed")
        return True
    except ImportError:
        if optional:
            print(f"⚠ {module_name} is NOT installed (optional)")
        else:
            print(f"❌ {module_name} is NOT installed (required)")
        return not optional

def check_tesseract():
    """Check if Tesseract OCR is installed."""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract OCR is installed (version {version})")
        return True
    except Exception:
        print("⚠ Tesseract OCR is NOT installed (optional for receipt scanning)")
        print("  Install: sudo apt-get install tesseract-ocr (Ubuntu/Debian)")
        print("           brew install tesseract (macOS)")
        return False

def main():
    """Run all dependency checks."""
    print("=" * 60)
    print("Personal Accounting App - Dependency Checker")
    print("=" * 60)
    print()

    all_good = True

    # Check Python version
    print("Checking Python version...")
    all_good &= check_python_version()
    print()

    # Check required Python packages
    print("Checking required Python packages...")
    all_good &= check_module("tkinter")
    all_good &= check_module("sqlite3")
    all_good &= check_module("Pillow", "PIL")
    all_good &= check_module("pytesseract")
    all_good &= check_module("PyPDF2")
    print()

    # Check optional system dependencies
    print("Checking optional system dependencies...")
    tesseract_ok = check_tesseract()
    print()

    # Summary
    print("=" * 60)
    if all_good:
        print("✓ All required dependencies are installed!")
        print()
        print("Run the app with: python accounting_app.py")

        if not tesseract_ok:
            print()
            print("Note: Receipt scanning will not work without Tesseract OCR.")
            print("      All other features will work normally.")
    else:
        print("❌ Some required dependencies are missing.")
        print()
        print("Install Python packages with:")
        print("  pip install -r requirements.txt")
        print()
        print("Install tkinter (if missing):")
        print("  Ubuntu/Debian: sudo apt-get install python3-tk")
        print("  Fedora: sudo dnf install python3-tkinter")

    print("=" * 60)
    print()

    # Important note about the type of application
    print("IMPORTANT NOTE:")
    print("This is a DESKTOP GUI application using tkinter.")
    print("It is NOT a web application and does NOT run on localhost:8000.")
    print("To use the app, run: python accounting_app.py")
    print("A window will appear on your desktop.")
    print()

    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
