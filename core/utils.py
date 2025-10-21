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
    If sms is not configured, it logs and returns None (useful for tests/dev).
    """
    if not to_number:
        logger.warning("No recipient phone number provided.")
        return None

    if not sms:
        logger.info("[TEST MODE] Would send SMS to %s: %s", to_number, message)
        return {
            "status": "simulated",
            "to": to_number,
            "message": message,
        }

    try:
        response = sms.send(message, [to_number])
        logger.info("SMS sent: %s", response)
        return response
    except Exception as e:
        logger.exception("Failed to send SMS")
        return None
