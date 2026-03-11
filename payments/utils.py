import requests
import base64
from datetime import datetime
from requests.auth import HTTPBasicAuth
from django.conf import settings

def get_mpesa_access_token():
    """
    This function talks to Safaricom, hands them your Consumer Key and Secret, 
    and returns a temporary 1-hour Access Token so you can trigger payments.
    """
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    
    # The official Safaricom Sandbox URL for generating tokens
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    
    try:
        # We use the 'requests' library we just installed to ping Safaricom
        response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        
        # Safaricom sends back a JSON response. We extract just the token string.
        mpesa_access_token = response.json()['access_token']
        return mpesa_access_token
        
    except Exception as e:
        print(f"Error getting M-Pesa token: {e}")
        return None

def generate_stk_password():
    """
    Generates the unique, time-stamped encrypted password required for an STK Push.
    """
    # Get the current time in the exact format Safaricom demands: YYYYMMDDHHmmss
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # Mash the Shortcode, Passkey, and Timestamp together
    data_to_encode = settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp
    
    # Encrypt it into Base64 format
    encoded_string = base64.b64encode(data_to_encode.encode())
    decoded_password = encoded_string.decode('utf-8')
    
    return decoded_password, timestamp        

def trigger_stk_push(phone_number, amount, order_id):
    """
    Sends the actual STK Push request to the customer's phone.
    """
    # 1. Grab the keys we just built
    access_token = get_mpesa_access_token()
    password, timestamp = generate_stk_password()
    
    if not access_token:
        return {"error": "Failed to generate access token"}

    # 2. The official Safaricom Sandbox URL for STK Pushes
    api_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    
    # 3. We use the access token as our VIP pass in the headers
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # 4. We package up the exact data Safaricom requires
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount), # M-Pesa requires the amount to be a whole number!
        "PartyA": phone_number, # The customer's phone number (Must be format: 2547XXXXXXXX)
        "PartyB": settings.MPESA_SHORTCODE, # The business receiving the money
        "PhoneNumber": phone_number,
        
        # NOTE: Safaricom needs a public internet URL to send the "Success" or "Failed" receipt to. 
        "CallBackURL": "https://sandbox.safaricom.co.ke/test_callback", 
        
        "AccountReference": f"Order {order_id}",
        "TransactionDesc": "Payment for Nyar Gi Jack Sound Gear"
    }
    
    # 5. Fire the request!
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        print(f"STK Push Error: {e}")
        return {"error": str(e)}