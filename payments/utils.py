"""
payments/utils.py — Production-hardened M-Pesa Daraja API utilities.

Fixes from original:
  1. CallBackURL was hardcoded to Safaricom's test sink — real callbacks never fired
  2. API URLs always hit sandbox even when MPESA_ENVIRONMENT=production
  3. print() replaced with proper logging — visible in Render's log dashboard
  4. Timeouts added — original had no timeout, a slow Safaricom response
     would hang your web worker indefinitely
  5. HTTP error status codes now caught and logged
"""

import requests
import base64
import logging
from datetime import datetime
from requests.auth import HTTPBasicAuth
from django.conf import settings

logger = logging.getLogger('payments')

# ─── API URLs ─────────────────────────────────────────────────────────────────
MPESA_URLS = {
    'sandbox': {
        'auth':     'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials',
        'stk_push': 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest',
    },
    'production': {
        'auth':     'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials',
        'stk_push': 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest',
    },
}


def _get_urls():
    """Return the correct API URLs based on MPESA_ENVIRONMENT setting."""
    env = getattr(settings, 'MPESA_ENVIRONMENT', 'sandbox')
    return MPESA_URLS.get(env, MPESA_URLS['sandbox'])


def get_mpesa_access_token():
    """
    Fetches a short-lived OAuth token from Safaricom.
    Valid for 1 hour. Called fresh on every STK Push (stateless, simple).
    For high-traffic systems, cache this token in Redis instead.
    """
    urls = _get_urls()

    try:
        response = requests.get(
            urls['auth'],
            auth=HTTPBasicAuth(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET),
            timeout=10,   # Don't hang forever if Safaricom is slow
        )
        response.raise_for_status()   # Raises on 4xx/5xx — caught below

        token = response.json().get('access_token')
        if not token:
            logger.error('M-Pesa auth response missing access_token: %s', response.text)
            return None

        logger.debug('M-Pesa access token fetched successfully')
        return token

    except requests.exceptions.Timeout:
        logger.error('M-Pesa token request timed out')
        return None
    except requests.exceptions.HTTPError as e:
        logger.error('M-Pesa token HTTP error: %s — %s', e.response.status_code, e.response.text)
        return None
    except requests.exceptions.RequestException as e:
        logger.error('M-Pesa token request failed: %s', e)
        return None


def generate_stk_password():
    """
    Generates the time-stamped Base64 password Safaricom requires.
    Format: Base64(Shortcode + Passkey + Timestamp)
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    raw = settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp
    password = base64.b64encode(raw.encode()).decode('utf-8')
    return password, timestamp


def trigger_stk_push(phone_number, amount, order_id):
    """
    Sends an STK Push request to the customer's phone.

    Args:
        phone_number (str): Customer number in 2547XXXXXXXX format
        amount (int):       Amount in KES (whole number, no decimals)
        order_id (int):     Order ID used as the payment reference

    Returns:
        dict: Safaricom's response JSON, or an error dict on failure
    """
    access_token = get_mpesa_access_token()

    if not access_token:
        return {'error': 'Failed to obtain M-Pesa access token. Check credentials.'}

    password, timestamp = generate_stk_password()
    urls = _get_urls()

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    payload = {
        'BusinessShortCode': settings.MPESA_SHORTCODE,
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': 'CustomerPayBillOnline',
        'Amount': int(amount),
        'PartyA': phone_number,
        'PartyB': settings.MPESA_SHORTCODE,
        'PhoneNumber': phone_number,
        # ✅ FIX: pulled from settings — works locally (ngrok) and on Render
        'CallBackURL': settings.MPESA_CALLBACK_URL,
        'AccountReference': f'Order-{order_id}',
        'TransactionDesc': f'Nyar Gi Jack Sound — Order {order_id}',
    }

    logger.info(
        'STK Push → Order #%s | Phone: %s | Amount: KES %s | Env: %s',
        order_id, phone_number, amount, settings.MPESA_ENVIRONMENT
    )

    try:
        response = requests.post(
            urls['stk_push'],
            json=payload,
            headers=headers,
            timeout=15,   # STK push can be slower than auth
        )
        response.raise_for_status()

        data = response.json()
        logger.info('STK Push response for Order #%s: %s', order_id, data)
        return data

    except requests.exceptions.Timeout:
        logger.error('STK Push timed out for Order #%s', order_id)
        return {'error': 'M-Pesa request timed out. Please try again.'}
    except requests.exceptions.HTTPError as e:
        logger.error('STK Push HTTP error for Order #%s: %s', order_id, e.response.text)
        return {'error': f'M-Pesa error: {e.response.status_code}'}
    except requests.exceptions.RequestException as e:
        logger.error('STK Push request failed for Order #%s: %s', order_id, e)
        return {'error': str(e)}
