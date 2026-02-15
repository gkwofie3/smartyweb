from django.conf import settings
try:
    from Zenoph.Notify.Enums.AuthModel import AuthModel
    from Zenoph.Notify.Enums.SMSType import SMSType
    from Zenoph.Notify.Request.CreditBalanceRequest import CreditBalanceRequest
    from Zenoph.Notify.Request.SMSRequest import SMSRequest
except ImportError:
    # Fallback to dummy if lib not found during initialization
    AuthModel = SMSType = CreditBalanceRequest = SMSRequest = None

import logging

logger = logging.getLogger(__name__)

API_HOST = "api.smsonlinegh.com"

def send_sms(recipient, message):
    if not all([AuthModel, SMSType, SMSRequest]):
        logger.error("SMS library not loaded properly.")
        return False
        
    try:
        # Check Balance (Optional but recommended)
        balance_req = CreditBalanceRequest()
        balance_req.setHost(API_HOST)
        balance_req.setAuthModel(AuthModel.API_KEY)
        balance_req.setAuthApiKey(settings.SMS_API_KEY)
        
        balance_resp = balance_req.submit()
        if float(balance_resp.getBalance()) <= 0:
            logger.warning("Insufficient SMS balance.")
            # We still try to send or just return? User usually wants to know.
            
        sms_req = SMSRequest()
        sms_req.setHost(API_HOST)
        sms_req.setAuthModel(AuthModel.API_KEY)
        sms_req.setAuthApiKey(settings.SMS_API_KEY)
        
        sms_req.setMessage(message)
        sms_req.setSMSType(SMSType.GSM_DEFAULT)
        sms_req.setSender("Smarty")
        sms_req.addDestination(recipient)
        
        sms_req.submit()
        return True
    except Exception as e:
        logger.error(f"Error sending SMS: {e}")
        return False
