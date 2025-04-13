#!/usr/bin/env python3
import requests
import re
import os
import json
from PIL import Image
import io
import time

# Configuration
base_url = 'http://localhost:5090'  # Using our updated port
admin_user = {'username': 'admin', 'password': 'admin123'}

def generate_test_image(filename, size=(300, 200), color=(50, 100, 150)):
    """Generate a test image for upload testing"""
    img = Image.new('RGB', size, color=color)
    img.save(filename)
    return filename

def test_admin_landing_page():
    # Start a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Login as admin
    print("Logging in as admin...")
    login_response = session.post(
        f'{base_url}/login',
        data=admin_user,
        allow_redirects=True
    )
    
    if '/admin' not in login_response.url:
        print(f"Login failed! Redirected to {login_response.url}")
        return False
    
    print(f"Login successful! Redirected to {login_response.url}")
    
    # Step 2: Access the admin landing page editor
    print("\nAccessing landing page editor...")
    landing_page_response = session.get(f'{base_url}/admin/landing_page')
    
    if landing_page_response.status_code != 200:
        print(f"Failed to access landing page editor. Status: {landing_page_response.status_code}")
        return False
    
    # Check if we got the editor page
    if "Landing Page Editor" not in landing_page_response.text:
        print("The page doesn't appear to be the landing page editor")
        return False
        
    print("Successfully accessed landing page editor")
    
    # Step 3: Find the form action for page background
    page_bg_form_action = None
    pattern = r'<form method="post" action="([^"]+)"[^>]*>\s*<input type="hidden" name="section" value="page">'
    match = re.search(pattern, landing_page_response.text)
    
    if match:
        page_bg_form_action = match.group(1)
        print(f"Found page background form action: {page_bg_form_action}")
    else:
        print("Could not find the page background form action")
        # Fall back to default
        page_bg_form_action = '/admin/landing_page/save2'
    
    # Step 4: Generate a test image
    test_image = "test_page_bg_image.png"
    generate_test_image(test_image)
    print(f"Generated test image: {test_image}")
    
    # Step 5: Submit the form with the test image
    print("\nSubmitting page background form...")
    
    # Prepare files and form data
    with open(test_image, 'rb') as f:
        files = {'page_bg_image': (test_image, f, 'image/png')}
        data = {
            'section': 'page',
            'page_bg_color': '#ffffff',
            'content_bg_color': '#ffffff',
            'content_text_color': '#212529'
        }
        
        # Build the full URL
        if page_bg_form_action.startswith(('http://', 'https://')):
            form_url = page_bg_form_action
        elif page_bg_form_action.startswith('/'):
            form_url = f"{base_url}{page_bg_form_action}"
        else:
            form_url = f"{base_url}/{page_bg_form_action}"
            
        print(f"Posting to: {form_url}")
        
        # Submit the form
        response = session.post(form_url, files=files, data=data)
        print(f"Form submission response: {response.status_code}")
        
        # Check if redirected back to editor page
        if "Landing Page Editor" in response.text and response.status_code == 200:
            print("Successfully redirected back to editor page")
        else:
            print("Form submission didn't redirect back to editor as expected")
            
        # Get the current bg_image URL from the page
        bg_image_pattern = r'Background Image: (img/custom/[^\s<]+)'
        bg_match = re.search(bg_image_pattern, response.text)
        
        if bg_match:
            bg_image_url = bg_match.group(1)
            print(f"Found new background image URL: {bg_image_url}")
            
            # Try to verify the image exists
            image_response = session.get(f"{base_url}/static/{bg_image_url}")
            if image_response.status_code == 200:
                print("Successfully verified the image was uploaded and accessible")
                print(f"Image size: {len(image_response.content)} bytes")
            else:
                print(f"Could not access the uploaded image. Status: {image_response.status_code}")
        else:
            print("Could not find background image in the response")
    
    # Clean up
    if os.path.exists(test_image):
        os.remove(test_image)
        
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Testing admin landing page background upload functionality")
    print("=" * 60)
    test_admin_landing_page()
    print("\nTest completed!")