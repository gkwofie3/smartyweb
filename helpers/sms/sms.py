import json
import http.client as httpClient
import logging

logger = logging.getLogger(__name__)

API_KEY = '4d94779e03f1a55e06b849bb42710b568c2f3779781788425994bb8916b33f21'

class SMS:
    def __init__(self, api_key=None):
        self.host = 'api.smsonlinegh.com'
        self.api_key = api_key or API_KEY
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
                return {"status": "success", "message": f"SMS sent successfully to {recipient}!"}
            else:
                return {"status": "error", "message": f"Request failed with status {status}: {response_data}"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

def send_sms(recipient, message, sender=None):
    sms = SMS()
    return sms.send_sms(recipient, message, sender)