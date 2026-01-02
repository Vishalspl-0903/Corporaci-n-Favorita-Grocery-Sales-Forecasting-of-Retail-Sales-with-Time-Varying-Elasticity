"""
Environment Check Script
Verifies all dependencies and configurations are properly set up
"""
import sys
import subprocess


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("⚠ Warning: Python 3.8+ is recommended")
        return False
    return True


def check_java():
    """Check Java installation"""
    try:
        result = subprocess.run(['java', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✓ Java is installed")
            return True
        else:
            print("✗ Java not found")
            return False
    except Exception as e:
        print(f"✗ Java not found: {e}")
        print("  PySpark requires Java 8 or 11")
        print("  Please install Java and set JAVA_HOME")
        return False


def check_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✓ {package_name} is installed")
        return True
    except ImportError:
        print(f"✗ {package_name} is NOT installed")
        return False


def main():
    """Run all checks"""
    print("="*60)
    print("ENVIRONMENT CHECK")
    print("="*60)
    
    checks = []
    
    # Python version
    print("\n1. Python Version:")
    checks.append(check_python_version())
    
    # Java
    print("\n2. Java:")
    checks.append(check_java())
    
    # Required packages
    print("\n3. Required Python Packages:")
    packages = [
        ('pyspark', 'pyspark'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('scikit-learn', 'sklearn'),
        ('tensorflow', 'tensorflow'),
        ('statsmodels', 'statsmodels'),
        ('matplotlib', 'matplotlib'),
        ('seaborn', 'seaborn'),
        ('pyarrow', 'pyarrow'),
    ]
    
    for package_name, import_name in packages:
        checks.append(check_package(package_name, import_name))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(checks)
    total = len(checks)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All checks passed! You're ready to run the pipeline.")
    else:
        print("\n⚠ Some checks failed. Please install missing dependencies.")
        print("\nTo install all packages:")
        print("  pip install -r requirements.txt")
    
    print("="*60)


if __name__ == "__main__":
    main()
