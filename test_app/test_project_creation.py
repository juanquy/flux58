#!/usr/bin/env python3
import requests
import re
import json
from urllib.parse import urlparse
import time

# Configuration
base_url = 'http://localhost:5090'
test_user = {'username': 'test', 'password': 'test123'}

# Function to log in and get a session
def login(credentials):
    session = requests.Session()
    
    # Make a GET request to the login page
    login_get = session.get(f'{base_url}/login')
    print(f"Initial GET request to /login: Status {login_get.status_code}")
    
    # Prepare login data
    login_data = credentials.copy()
    
    # Make login request
    print(f"\nLogging in as {credentials['username']} with password {credentials['password']}")
    login_response = session.post(
        f'{base_url}/login', 
        data=login_data,
        allow_redirects=True
    )
    
    print(f"Login response: Status {login_response.status_code}")
    
    # Check if we're logged in by looking for username in the response
    if credentials['username'] in login_response.text:
        print(f"Successfully logged in as {credentials['username']}")
        return session
    else:
        print("Login failed")
        return None

# Function to create a project
def create_project(session, project_name="Test Project", description="Created by automated test"):
    # First get the form
    form_response = session.get(f'{base_url}/projects/new')
    print(f"Getting project form: Status {form_response.status_code}")
    
    if form_response.status_code != 200:
        print("Failed to get project creation form")
        return None
    
    # Prepare project data
    project_data = {
        'name': project_name,
        'description': description,
        'resolution': '1080p',
        'framerate': '30'
    }
    
    # Submit the form
    create_response = session.post(
        f'{base_url}/projects/new',
        data=project_data,
        allow_redirects=True
    )
    
    print(f"Project creation response: Status {create_response.status_code}")
    
    # Check if we were redirected to editor
    if '/editor' in create_response.url:
        print(f"Successfully created project and redirected to {create_response.url}")
        
        # Extract project ID from URL
        url_parts = urlparse(create_response.url)
        query_params = url_parts.query.split('&')
        project_id = None
        
        for param in query_params:
            if param.startswith('project_id='):
                project_id = param.split('=')[1]
                break
        
        return project_id
    else:
        print("Project creation may have failed, not redirected to editor")
        print(f"Current URL: {create_response.url}")
        
        # Check for error message in response
        if "Error" in create_response.text:
            error_match = re.search(r'<div class="alert alert-danger">(.*?)</div>', 
                                   create_response.text, re.DOTALL)
            if error_match:
                print(f"Error message: {error_match.group(1).strip()}")
        
        return None

# Main test flow
print("=" * 50)
print("Testing project creation:")

# 1. Login
session = login(test_user)
if not session:
    print("Failed to log in, cannot continue test")
    exit(1)

# 2. Create a project
project_id = create_project(session, 
                           project_name=f"Test Project {time.strftime('%Y-%m-%d %H:%M:%S')}", 
                           description="Created by automated test script")

# 3. Verify project exists if creation was successful
if project_id:
    print(f"Project created with ID: {project_id}")
    
    # Try to get project details
    project_response = session.get(f"{base_url}/projects/{project_id}")
    print(f"Project details page response: Status {project_response.status_code}")
    
    if project_response.status_code == 200:
        print("Project details page loaded successfully")
    else:
        print("Failed to load project details")
else:
    print("Failed to create project")

print("\nProject creation testing complete!")