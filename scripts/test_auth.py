#!/usr/bin/env python3
"""
Test script for authentication functionality
"""

import sqlite3
import requests
import sys
from werkzeug.security import check_password_hash

def test_database():
    """Test database setup and user creation"""
    print("🔍 Testing database setup...")
    
    try:
        conn = sqlite3.connect('teacher_ai.db')
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ Users table does not exist!")
            return False
        
        # Check admin user
        cursor.execute('SELECT username, password_hash, is_admin FROM users WHERE username = ?', ('admin',))
        admin = cursor.fetchone()
        
        if admin:
            print(f"✅ Admin user found: {admin[0]}")
            # Test password hash
            if check_password_hash(admin[1], 'admin123'):
                print("✅ Admin password hash is correct")
            else:
                print("❌ Admin password hash is incorrect")
        else:
            print("❌ Admin user not found!")
            return False
        
        # Check sample users
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0')
        user_count = cursor.fetchone()[0]
        print(f"✅ Found {user_count} regular users")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_flask_app():
    """Test if Flask app is running"""
    print("\n🔍 Testing Flask application...")
    
    try:
        response = requests.get('http://localhost:5000/', timeout=5)
        if response.status_code == 200:
            print("✅ Flask app is running and accessible")
            return True
        else:
            print(f"❌ Flask app returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def test_login_endpoint():
    """Test login endpoint"""
    print("\n🔍 Testing login endpoint...")
    
    try:
        # Test GET request to login page
        response = requests.get('http://localhost:5000/login', timeout=5)
        if response.status_code == 200:
            print("✅ Login page loads successfully")
        else:
            print(f"❌ Login page returned status code: {response.status_code}")
            return False
        
        # Test POST request with valid credentials
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        session = requests.Session()
        response = session.post('http://localhost:5000/login', data=login_data, timeout=5)
        
        if response.status_code == 200 or response.status_code == 302:
            print("✅ Login POST request successful")
            return True
        else:
            print(f"❌ Login POST failed with status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Login endpoint test failed: {e}")
        return False

def test_register_endpoint():
    """Test register endpoint"""
    print("\n🔍 Testing register endpoint...")
    
    try:
        # Test GET request to register page
        response = requests.get('http://localhost:5000/register', timeout=5)
        if response.status_code == 200:
            print("✅ Register page loads successfully")
        else:
            print(f"❌ Register page returned status code: {response.status_code}")
            return False
        
        # Test POST request with new user data
        register_data = {
            'username': f'testuser_{int(time.time())}',
            'email': f'test_{int(time.time())}@example.com',
            'password': 'testpassword123'
        }
        
        response = requests.post('http://localhost:5000/register', data=register_data, timeout=5)
        
        if response.status_code == 200 or response.status_code == 302:
            print("✅ Register POST request successful")
            return True
        else:
            print(f"❌ Register POST failed with status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Register endpoint test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Teacher AI Platform - Authentication Tests")
    print("=" * 50)
    
    tests = [
        ("Database Setup", test_database),
        ("Flask Application", test_flask_app),
        ("Login Endpoint", test_login_endpoint),
        ("Register Endpoint", test_register_endpoint)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed!")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Authentication system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    import time
    success = main()
    sys.exit(0 if success else 1)
