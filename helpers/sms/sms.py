API_KEY='4d94779e03f1a55e06b849bb42710b568c2f3779781788425994bb8916b33f21'

from Zenoph.Notify.Enums.AuthModel import AuthModel
from Zenoph.Notify.Enums.SMSType import SMSType
from Zenoph.Notify.Request.CreditBalanceRequest import CreditBalanceRequest
from Zenoph.Notify.Request.SMSRequest import SMSRequest

# Configuration Constants

API_HOST = "api.smsonlinegh.com"

def send_sms(recipient, sender, message):
    
    try:
        # 1. Initialize Balance Request
        balance_req = CreditBalanceRequest()
        balance_req.setHost(API_HOST)
        balance_req.setAuthModel(AuthModel.API_KEY)
        balance_req.setAuthApiKey(API_KEY)
        
        # Check Balance
        balance_resp = balance_req.submit()
        current_balance = float(balance_resp.getBalance())
                
        if current_balance <= 0:
            return {"status": "failed", "message": "Insufficient balance to send SMS."}

        # 2. Initialize SMS Request
        sms_req = SMSRequest()
        sms_req.setHost(API_HOST)
        sms_req.setAuthModel(AuthModel.API_KEY)
        sms_req.setAuthApiKey(API_KEY)
        
        # Set Message Details
        sms_req.setMessage(message)
        sms_req.setSMSType(SMSType.GSM_DEFAULT)
        sms_req.setSender(sender)
        sms_req.addDestination(recipient)
        
        # Submit SMS
        sms_resp = sms_req.submit()
        return {"status": "success", "message": f"SMS sent successfully to {recipient}!"}

    except Exception as e:
        return {"status": "error", "message": str(e)}