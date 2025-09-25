"""
Payment processors for flexible payment methods
"""
import requests
from abc import ABC, abstractmethod
from django.conf import settings
from decimal import Decimal


class PaymentProcessor(ABC):
    """Abstract base class for payment processors"""

    @abstractmethod
    def initiate_payment(self, order, phone_number):
        """Initiate a payment request"""
        pass

    @abstractmethod
    def confirm_payment(self, transaction_id):
        """Confirm payment status"""
        pass

    @abstractmethod
    def refund_payment(self, transaction_id, amount):
        """Refund a payment"""
        pass


class MpesaProcessor(PaymentProcessor):
    """M-Pesa payment processor"""

    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.base_url = settings.MPESA_BASE_URL

        if not all([self.consumer_key, self.consumer_secret, self.shortcode, self.passkey]):
            raise ValueError("M-Pesa credentials not configured. Please set MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET, MPESA_SHORTCODE, and MPESA_PASSKEY in your environment variables.")

    def get_access_token(self):
        """Get M-Pesa access token"""
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(url, auth=(self.consumer_key, self.consumer_secret))
        response.raise_for_status()
        return response.json()['access_token']

    def initiate_payment(self, order, phone_number):
        """Initiate STK Push for M-Pesa"""
        access_token = self.get_access_token()
        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        timestamp = self._get_timestamp()
        password = self._generate_password(timestamp)

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(order.total_amount),
            "PartyA": phone_number,
            "PartyB": self.shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": f"{settings.SITE_DOMAIN}/orders/mpesa/callback/",
            "AccountReference": f"Order {order.order_number}",
            "TransactionDesc": f"Payment for order {order.order_number}"
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    def confirm_payment(self, transaction_id):
        """Check payment status"""
        access_token = self.get_access_token()
        url = f"{self.base_url}/mpesa/stkpushquery/v1/query"

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        timestamp = self._get_timestamp()
        password = self._generate_password(timestamp)

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": transaction_id
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    def refund_payment(self, transaction_id, amount):
        """Refund payment (simplified)"""
        # M-Pesa refund logic would go here
        # For now, return success
        return {"ResponseCode": "0", "ResponseDescription": "Refund successful"}

    def _get_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime('%Y%m%d%H%M%S')

    def _generate_password(self, timestamp):
        import base64
        data = f"{self.shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(data.encode()).decode('utf-8')


# Factory function to get processor
def get_payment_processor(method):
    """Get payment processor based on method"""
    if method == 'mpesa':
        return MpesaProcessor()
    else:
        raise ValueError(f"Unsupported payment method: {method}")
