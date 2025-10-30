"""
Test script to verify GlowAura Candles setup
Run this from the Backend directory: python test_setup.py
"""
import os
import sys

def test_setup():
    print("🔍 Testing GlowAura Candles Setup...\n")
    
    errors = []
    warnings = []
    
    # Check Python files
    print("📁 Checking backend files...")
    required_files = {
        'main.py': 'Main FastAPI application',
        'models.py': 'Database models',
        'schemas.py': 'Pydantic schemas',
        'database.py': 'Database configuration',
    }
    
    for file, description in required_files.items():
        if os.path.exists(file):
            print(f"  ✓ {file} - {description}")
        else:
            errors.append(f"Missing: {file}")
            print(f"  ✗ {file} - MISSING!")
    
    # Check routes directory
    print("\n📁 Checking routes directory...")
    if os.path.exists('routes'):
        route_files = ['products.py', 'users.py', 'cart.py', 'orders.py', '__init__.py']
        for file in route_files:
            path = os.path.join('routes', file)
            if os.path.exists(path):
                print(f"  ✓ routes/{file}")
            else:
                errors.append(f"Missing: routes/{file}")
                print(f"  ✗ routes/{file} - MISSING!")
    else:
        errors.append("Missing: routes/ directory")
        print("  ✗ routes/ directory - MISSING!")
    
    # Check frontend directory
    print("\n📁 Checking frontend directory...")
    if os.path.exists('frontend'):
        html_files = ['index.html', 'product.html', 'cart.html', 'checkout.html', 
                      'login.html', 'register.html', 'admin.html']
        for file in html_files:
            path = os.path.join('frontend', file)
            if os.path.exists(path):
                print(f"  ✓ frontend/{file}")
            else:
                warnings.append(f"Missing: frontend/{file}")
                print(f"  ⚠ frontend/{file} - MISSING!")
    else:
        errors.append("Missing: frontend/ directory")
        print("  ✗ frontend/ directory - MISSING!")
    
    # Check static directory
    print("\n📁 Checking static directory...")
    if os.path.exists('static'):
        static_files = ['styles.css', 'scripts.js']
        for file in static_files:
            path = os.path.join('static', file)
            if os.path.exists(path):
                print(f"  ✓ static/{file}")
            else:
                errors.append(f"Missing: static/{file}")
                print(f"  ✗ static/{file} - MISSING!")
        
        # Check uploads directory
        if os.path.exists('static/uploads'):
            print(f"  ✓ static/uploads/")
        else:
            warnings.append("Missing: static/uploads/ directory")
            print(f"  ⚠ static/uploads/ - will be created automatically")
    else:
        errors.append("Missing: static/ directory")
        print("  ✗ static/ directory - MISSING!")
    
    # Check dependencies
    print("\n📦 Checking Python packages...")
    try:
        import fastapi
        print(f"  ✓ fastapi {fastapi.__version__}")
    except ImportError:
        errors.append("Missing package: fastapi")
        print("  ✗ fastapi - NOT INSTALLED!")
    
    try:
        import uvicorn
        print(f"  ✓ uvicorn")
    except ImportError:
        errors.append("Missing package: uvicorn")
        print("  ✗ uvicorn - NOT INSTALLED!")
    
    try:
        import sqlalchemy
        print(f"  ✓ sqlalchemy {sqlalchemy.__version__}")
    except ImportError:
        errors.append("Missing package: sqlalchemy")
        print("  ✗ sqlalchemy - NOT INSTALLED!")
    
    try:
        from jose import jwt
        print(f"  ✓ python-jose")
    except ImportError:
        errors.append("Missing package: python-jose")
        print("  ✗ python-jose - NOT INSTALLED!")
    
    # Summary
    print("\n" + "="*60)
    if errors:
        print("❌ ERRORS FOUND:")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print("\n⚠ WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")
    
    if not errors and not warnings:
        print("✅ ALL CHECKS PASSED!")
        print("\n🚀 You can now run the server:")
        print("   uvicorn main:app --reload")
        print("\n🌐 Then open: http://localhost:8000")
    elif not errors:
        print("✅ SETUP IS GOOD (with minor warnings)")
        print("\n🚀 You can now run the server:")
        print("   uvicorn main:app --reload")
        print("\n🌐 Then open: http://localhost:8000")
    else:
        print("\n❌ Please fix the errors above before running the server.")
        print("\n📖 Check README.md for setup instructions.")
    
    print("="*60)

if __name__ == "__main__":
    test_setup()