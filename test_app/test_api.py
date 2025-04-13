#!/usr/bin/env python3
"""
Test script for OpenShot SaaS API
This script performs basic API tests to verify functionality.
"""

import requests
import json
import sys
import time

# API base URL
BASE_URL = "http://localhost:5000/api"

def print_response(response):
    """Print formatted response for debugging"""
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print("-" * 40)

def test_api():
    """Run through basic API tests"""
    # Test 1: Check API info endpoint
    print("\n📡 Testing API Info...")
    response = requests.get(f"{BASE_URL}/info")
    print_response(response)
    
    # Test 2: Register new user
    print("\n👤 Registering new user...")
    user_data = {
        "username": f"testuser_{int(time.time())}",
        "password": "testpassword123",
        "email": "test@example.com"
    }
    response = requests.post(f"{BASE_URL}/register", json=user_data)
    print_response(response)
    
    if response.status_code != 201:
        print("❌ User registration failed! Exiting tests.")
        return
    
    # Test 3: Login
    print("\n🔑 Logging in...")
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print_response(response)
    
    if response.status_code != 200:
        print("❌ Login failed! Exiting tests.")
        return
    
    # Save token for authenticated requests
    token = response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 4: Add credits
    print("\n💰 Adding credits...")
    credit_data = {"amount": 100}
    response = requests.post(f"{BASE_URL}/payment/add-credits", 
                            headers=headers, json=credit_data)
    print_response(response)
    
    # Test 5: Check credit balance
    print("\n💳 Checking credit balance...")
    response = requests.get(f"{BASE_URL}/credits/balance", headers=headers)
    print_response(response)
    
    # Test 6: Create a project
    print("\n📁 Creating project...")
    project_data = {
        "name": "Test Project",
        "description": "A test project created by the API test script"
    }
    response = requests.post(f"{BASE_URL}/projects", headers=headers, json=project_data)
    print_response(response)
    
    if response.status_code != 201:
        print("❌ Project creation failed! Exiting tests.")
        return
    
    project_id = response.json()["project"]["id"]
    
    # Test 7: Get project details
    print("\n📋 Getting project details...")
    response = requests.get(f"{BASE_URL}/projects/{project_id}", headers=headers)
    print_response(response)
    
    # Test 8: List all projects
    print("\n📊 Listing all projects...")
    response = requests.get(f"{BASE_URL}/projects", headers=headers)
    print_response(response)
    
    # Test 9: Update project
    print("\n✏️ Updating project...")
    update_data = {
        "name": "Updated Test Project",
        "description": "This project was updated via the API"
    }
    response = requests.put(f"{BASE_URL}/projects/{project_id}", 
                           headers=headers, json=update_data)
    print_response(response)
    
    # Note: We're skipping file upload tests as they require multipart form data
    
    # Test 10: Logout
    print("\n🚪 Logging out...")
    response = requests.post(f"{BASE_URL}/logout", headers=headers)
    print_response(response)
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    print("🧪 Starting OpenShot SaaS API Test Script")
    print("=" * 50)
    test_api()