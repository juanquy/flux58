#!/usr/bin/env python3
import requests

# Test direct image access
def test_image_access(image_path):
    # Try to access the image directly
    url = f"http://localhost:5090/static/{image_path}"
    print(f"Testing access to URL: {url}")
    response = requests.get(url)
    
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print(f"Image size: {len(response.content)} bytes")
        print("Image is accessible!")
        return True
    else:
        print(f"Failed to access image: {response.status_code}")
        return False

if __name__ == "__main__":
    # Test the last uploaded background image
    image_path = "img/custom/page_bg_1742593039.png"
    test_image_access(image_path)