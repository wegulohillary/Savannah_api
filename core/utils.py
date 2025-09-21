from decouple import config
import logging

logger = logging.getLogger(__name__)

# Africa's Talking initialization
try:
    import africastalking
    AT_USERNAME = config('AFRICASTALKING_USERNAME', default=None)
    AT_API_KEY = config('AFRICASTALKING_API_KEY', default=None)
    if AT_USERNAME and AT_API_KEY:
        africastalking.initialize(AT_USERNAME, AT_API_KEY)
        sms = africastalking.SMS
    else:
        sms = None
except Exception:
    sms = None

def send_sms(to_number: str, message: str):
    """
    Send an SMS using Africa's Talking.
    to_number should be in international format, e.g., +2547XXXXXXXX.
    If sms is not configured, it logs and returns None for test/dev.
    """
    if not sms:
        logger.warning("Africa's Talking SMS client not configured. Would send to %s: %s", to_number, message)
        return None

    try:
        response = sms.send(message, [to_number])
        logger.info("SMS sent: %s", response)
        return response
    except Exception as e:
        logger.exception("Failed to send SMS")
        return None
