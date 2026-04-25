import json
import http.client as httpClient
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SMS:
    def __init__(self, api_key=None):
        self.host = 'api.smsonlinegh.com'
        self.api_key = api_key or getattr(settings, 'SMS_API_KEY', '')
        self.request_uri = '/v5/message/sms/send'

    def send_sms(self, recipient, message, sender=None):
        sender = sender or "Smarty"
        try:
            headers = {
                'Host': self.host,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'key {self.api_key}'
            }

            msg_data = {
                'text': message,
                'type': 0,
                'sender': sender,
                'destinations': [recipient] if isinstance(recipient, str) else recipient
            }

            http_conn = httpClient.HTTPSConnection(self.host)
            http_conn.request('POST', self.request_uri, json.dumps(msg_data), headers)

            response = http_conn.getresponse()
            status = response.status
            response_data = response.read().decode('utf-8')

            if status == 200:
                logger.info(f"SMS sent successfully to {recipient}!")
                return True
            else:
                logger.error(f"SMS request failed with status {status}: {response_data}")
                return False

        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False

def send_sms(recipient, message, sender=None):
    sms = SMS()
    return sms.send_sms(recipient, message, sender)

