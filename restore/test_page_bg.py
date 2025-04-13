import requests
import os
from io import BytesIO
from PIL import Image

# Create a test image
def create_test_image(filename):
    # Create a simple test image - a small colored rectangle
    img = Image.new('RGB', (200, 100), color=(73, 109, 137))
    img.save(filename)
    return filename

# Test file upload
def test_page_bg_upload():
    # Create a test image
    test_image = "test_bg_image.png"
    create_test_image(test_image)
    
    # URL for the landing page save endpoint
    url = 'http://localhost:5090/admin/landing_page/save'
    
    # Prepare files and form data
    with open(test_image, 'rb') as f:
        files = {'page_bg_image': (test_image, f, 'image/png')}
        data = {
            'section': 'page',
            'page_bg_color': '#ffffff',
            'content_bg_color': '#ffffff',
            'content_text_color': '#212529'
        }
        
        # First try to log in
        session = requests.Session()
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'remember': 'on'
        }
        
        login_response = session.post('http://localhost:5090/login_submit', data=login_data)
        print(f"Login response: {login_response.status_code}")
        
        # Now try to upload the background image
        response = session.post(url, files=files, data=data)
        print(f"Upload response: {response.status_code}")
        print(f"Response content: {response.text[:100]}...")  # Show first 100 chars
        
        # Check if redirected to the editor page
        if response.history:
            print(f"Redirected from {response.history[0].url} to {response.url}")
        
    # Clean up the test image
    if os.path.exists(test_image):
        os.remove(test_image)

if __name__ == "__main__":
    test_page_bg_upload()