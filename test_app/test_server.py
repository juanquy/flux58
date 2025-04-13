import requests

try:
    # Make a request to the server
    response = requests.get('http://localhost:5090')
    print(f"Server is accessible. Status code: {response.status_code}")
    print(f"Content length: {len(response.text)} bytes")
except Exception as e:
    print(f"Error connecting to server: {e}")