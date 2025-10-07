import requests
from django.conf import settings

PAYSTACK_BASE_URL = "https://api.paystack.co"

def initialize_payment(amount, email, reference, callback_url):
    url = f"{PAYSTACK_BASE_URL}/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "amount": int(amount * 100),  # Paystack uses kobo
        "email": email,
        "reference": reference,
        "callback_url": callback_url
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()['data']

def verify_payment(reference):
    url = f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']