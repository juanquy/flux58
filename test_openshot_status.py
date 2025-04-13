#!/usr/bin/env python3
import requests
import json

# Test the OpenShot status API
try:
    response = requests.get('http://localhost:5090/api/openshot/status')
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {str(e)}")