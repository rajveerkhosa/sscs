#!/usr/bin/env python3
"""
Quick .env file verification script
Checks if your .env file is properly formatted for SSCS scraper
"""

import os
from pathlib import Path


def check_env_file():
    """Check if .env file exists and is properly formatted"""

    print("=" * 60)
    print(".env File Verification")
    print("=" * 60)
    print()

    # Check if .env exists
    env_path = Path(".env")
    if not env_path.exists():
        print("✗ .env file not found!")
        print()
        print("To create it:")
        print("  1. Copy the template:")
        print("     cp .env.template .env")
        print()
        print("  2. Edit .env and add your credentials:")
        print("     SSCS_USER=your_username")
        print("     SSCS_PASS=your_password")
        print()
        print("IMPORTANT:")
        print("  - No quotes around values")
        print("  - No spaces around the = sign")
        print("  - One variable per line")
        print()
        return False

    print("✓ .env file exists")
    print()

    # Read and check contents
    print("Reading .env file...")
    print()

    with open(".env", "r") as f:
        lines = f.readlines()

    found_user = False
    found_pass = False
    issues = []

    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()

        # Skip empty lines and comments
        if not line_stripped or line_stripped.startswith("#"):
            continue

        # Check for SSCS_USER
        if line_stripped.startswith("SSCS_USER"):
            found_user = True

            # Check format
            if "=" not in line_stripped:
                issues.append(f"Line {i}: Missing = sign in SSCS_USER")
            elif " = " in line_stripped:
                issues.append(f"Line {i}: Remove spaces around = in SSCS_USER")
            elif line_stripped.count("=") > 1:
                issues.append(f"Line {i}: Multiple = signs in SSCS_USER")
            else:
                # Extract value
                value = line_stripped.split("=", 1)[1].strip()

                if not value:
                    issues.append(f"Line {i}: SSCS_USER has no value")
                elif value.startswith('"') or value.startswith("'"):
                    issues.append(f"Line {i}: Remove quotes from SSCS_USER value")
                elif value == "your_username_here" or value == "your_username":
                    issues.append(f"Line {i}: SSCS_USER still has placeholder value")
                else:
                    print(f"✓ SSCS_USER is set to: {value[:3]}***")

        # Check for SSCS_PASS
        if line_stripped.startswith("SSCS_PASS"):
            found_pass = True

            # Check format
            if "=" not in line_stripped:
                issues.append(f"Line {i}: Missing = sign in SSCS_PASS")
            elif " = " in line_stripped:
                issues.append(f"Line {i}: Remove spaces around = in SSCS_PASS")
            elif line_stripped.count("=") > 1:
                issues.append(f"Line {i}: Multiple = signs in SSCS_PASS")
            else:
                # Extract value
                value = line_stripped.split("=", 1)[1].strip()

                if not value:
                    issues.append(f"Line {i}: SSCS_PASS has no value")
                elif value.startswith('"') or value.startswith("'"):
                    issues.append(f"Line {i}: Remove quotes from SSCS_PASS value")
                elif value == "your_password_here" or value == "your_password":
                    issues.append(f"Line {i}: SSCS_PASS still has placeholder value")
                else:
                    print(f"✓ SSCS_PASS is set (length: {len(value)} characters)")

    print()

    # Check if both variables found
    if not found_user:
        issues.append("SSCS_USER not found in .env file")
    if not found_pass:
        issues.append("SSCS_PASS not found in .env file")

    # Report issues
    if issues:
        print("✗ Issues found:")
        print()
        for issue in issues:
            print(f"  • {issue}")
        print()
        print("Expected format:")
        print("  SSCS_USER=actual_username")
        print("  SSCS_PASS=actual_password")
        print()
        print("Example .env file:")
        print("-" * 40)
        print("SSCS_USER=john.doe")
        print("SSCS_PASS=MyP@ssw0rd123")
        print("-" * 40)
        print()
        print("Common mistakes to avoid:")
        print("  ✗ SSCS_USER = \"john.doe\"     (spaces and quotes)")
        print("  ✗ SSCS_USER='john.doe'        (quotes)")
        print("  ✗ SSCS_USER = john.doe        (spaces)")
        print("  ✓ SSCS_USER=john.doe          (correct!)")
        print()
        return False

    # All good
    print("✓ .env file looks good!")
    print()
    print("Next step: Run the script with visible browser:")
    print("  HEADLESS=false python main.py")
    print()
    return True


def test_load_env():
    """Test loading .env with python-dotenv"""
    print("=" * 60)
    print("Testing .env loading")
    print("=" * 60)
    print()

    try:
        from dotenv import load_dotenv
        load_dotenv()

        user = os.getenv("SSCS_USER")
        password = os.getenv("SSCS_PASS")

        if user and password:
            print("✓ Credentials loaded successfully!")
            print(f"  Username: {user[:3]}***")
            print(f"  Password: ***{password[-3:]} (length: {len(password)})")
            print()
            return True
        else:
            print("✗ Failed to load credentials")
            if not user:
                print("  SSCS_USER not loaded")
            if not password:
                print("  SSCS_PASS not loaded")
            print()
            return False

    except ImportError:
        print("✗ python-dotenv not installed")
        print("  Install with: pip install python-dotenv")
        print()
        return False


if __name__ == "__main__":
    file_ok = check_env_file()

    if file_ok:
        test_load_env()

    print("=" * 60)
