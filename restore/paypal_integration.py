import os
import requests
import json
import uuid
from datetime import datetime, timedelta
import logging

# PayPal API configuration
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', 'YOUR_PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET', 'YOUR_PAYPAL_CLIENT_SECRET')
PAYPAL_BASE_URL = os.environ.get('PAYPAL_BASE_URL', 'https://api-m.sandbox.paypal.com')  # Use 'https://api-m.paypal.com' for production

class PayPalAPI:
    def __init__(self, client_id=None, client_secret=None, base_url=None):
        """Initialize PayPal API with credentials"""
        self.client_id = client_id or PAYPAL_CLIENT_ID
        self.client_secret = client_secret or PAYPAL_CLIENT_SECRET
        self.base_url = base_url or PAYPAL_BASE_URL
        self.access_token = None
        self.token_expires_at = None
        
    def _get_access_token(self):
        """Get OAuth 2.0 access token from PayPal"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
            
        url = f"{self.base_url}/v1/oauth2/token"
        auth = (self.client_id, self.client_secret)
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en_US"
        }
        data = {
            "grant_type": "client_credentials"
        }
        
        try:
            response = requests.post(url, auth=auth, headers=headers, data=data)
            response.raise_for_status()  # Raise exception on HTTP error
            
            result = response.json()
            self.access_token = result["access_token"]
            self.token_expires_at = datetime.now() + timedelta(seconds=result["expires_in"])
            
            return self.access_token
        except requests.exceptions.RequestException as e:
            logging.error(f"PayPal API error getting access token: {str(e)}")
            return None
    
    def create_order(self, amount, currency="USD", description="Purchase credits", return_url=None, cancel_url=None):
        """Create a PayPal order for a specific amount and return approval URL"""
        token = self._get_access_token()
        if not token:
            return None
            
        url = f"{self.base_url}/v2/checkout/orders"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": str(uuid.uuid4()),
                    "description": description,
                    "amount": {
                        "currency_code": currency,
                        "value": str(amount)
                    }
                }
            ],
            "application_context": {
                "return_url": return_url,
                "cancel_url": cancel_url,
                "brand_name": "FLUX58 AI MEDIA LABS",
                "landing_page": "BILLING",
                "user_action": "PAY_NOW"
            }
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            
            result = response.json()
            
            # Extract the approval URL (redirect URL for the user)
            for link in result["links"]:
                if link["rel"] == "approve":
                    return {
                        "id": result["id"],
                        "status": result["status"],
                        "approval_url": link["href"]
                    }
            
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"PayPal API error creating order: {str(e)}")
            return None
    
    def capture_order(self, order_id):
        """Capture an approved PayPal order (finalize the payment)"""
        token = self._get_access_token()
        if not token:
            return None
            
        url = f"{self.base_url}/v2/checkout/orders/{order_id}/capture"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            return {
                "id": result["id"],
                "status": result["status"],
                "payer": result.get("payer", {}),
                "amount": result["purchase_units"][0]["payments"]["captures"][0]["amount"]["value"],
                "currency": result["purchase_units"][0]["payments"]["captures"][0]["amount"]["currency_code"]
            }
        except requests.exceptions.RequestException as e:
            logging.error(f"PayPal API error capturing order: {str(e)}")
            return None
    
    def get_order_details(self, order_id):
        """Get details of a PayPal order"""
        token = self._get_access_token()
        if not token:
            return None
            
        url = f"{self.base_url}/v2/checkout/orders/{order_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"PayPal API error getting order details: {str(e)}")
            return None