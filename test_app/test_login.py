#!/usr/bin/env python3
import requests
import re
import json
from urllib.parse import urlparse
import time

# Configuration
base_url = 'http://localhost:5000'
admin_user = {'username': 'admin', 'password': 'admin123'}
test_user = {'username': 'test', 'password': 'test123'}

# Function to test login and follow redirects
def test_login_and_redirect(credentials):
    session = requests.Session()
    
    # First, make a GET request to the login page to get any CSRF token
    login_get = session.get(f'{base_url}/login')
    print(f"Initial GET request to /login: Status {login_get.status_code}")
    
    # Look for any CSRF token (not likely in this simple app, but good practice)
    csrf_token = None
    if 'csrf_token' in login_get.text:
        match = re.search(r'name="csrf_token" value="([^"]+)"', login_get.text)
        if match:
            csrf_token = match.group(1)
            print(f"Found CSRF token: {csrf_token[:10]}...")
    
    # Prepare login data
    login_data = credentials.copy()
    if csrf_token:
        login_data['csrf_token'] = csrf_token
    
    # Make login request
    print(f"\nLogging in as {credentials['username']} with password {credentials['password']}")
    login_response = session.post(
        f'{base_url}/login', 
        data=login_data,
        allow_redirects=False  # Don't follow redirects automatically
    )
    
    print(f"Login POST response: Status {login_response.status_code}")
    
    # Check if we got a redirect
    if 300 <= login_response.status_code < 400:
        redirect_url = login_response.headers.get('Location')
        print(f"Received redirect to: {redirect_url}")
        
        # Follow the redirect manually
        redirect_response = session.get(f"{base_url}{redirect_url}" if redirect_url.startswith('/') else redirect_url)
        print(f"Redirect response: Status {redirect_response.status_code}")
        
        # Extract page title to verify where we landed
        title_match = re.search(r'<title>(.*?)</title>', redirect_response.text)
        if title_match:
            page_title = title_match.group(1)
            print(f"Landed on page with title: {page_title}")
        
        # Check if we're still on the login page (which would indicate failure)
        if '/login' in redirect_response.url:
            print("ERROR: Still on login page after redirect - login failed!")
        else:
            print(f"SUCCESS: Redirected to {redirect_response.url}")
            
            # Dump cookies for debugging
            print("\nSession cookies:")
            for cookie in session.cookies:
                print(f"  {cookie.name}: {cookie.value[:10]}... (expires: {cookie.expires})")
                
            return redirect_response.url, session
    else:
        print(f"ERROR: No redirect received. Response: {login_response.text[:200]}")
        return None, session
    
    return None, session

# Test both user types
print("=" * 50)
print("Testing admin login:")
admin_redirect, admin_session = test_login_and_redirect(admin_user)

# Wait a moment between tests
time.sleep(1)

print("\n" + "=" * 50)
print("Testing regular user login:")
user_redirect, user_session = test_login_and_redirect(test_user)

# Verify expected redirect pages
print("\n" + "=" * 50)
print("SUMMARY:")
if admin_redirect and '/admin' in admin_redirect:
    print("✅ Admin login successfully redirected to admin dashboard")
else:
    print("❌ Admin login failed to redirect to admin dashboard")
    
if user_redirect and '/dashboard' in user_redirect:
    print("✅ User login successfully redirected to user dashboard")
else:
    print("❌ User login failed to redirect to user dashboard")

# Test logout if everything worked
print("\n" + "=" * 50)
if admin_redirect:
    print("Testing admin logout:")
    logout = admin_session.get(f"{base_url}/logout")
    print(f"Logout status: {logout.status_code}")
    print(f"Redirected to: {logout.url}")

print("\nLogin testing complete!")