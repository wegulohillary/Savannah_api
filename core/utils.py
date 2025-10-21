from decouple import config
import logging

logger = logging.getLogger(__name__)

# Africa's Talking initialization
try:
    import africastalking
    AT_USERNAME = config("AFRICASTALKING_USERNAME", default=None)
    AT_API_KEY = config("AFRICASTALKING_API_KEY", default=None)

    if AT_USERNAME and AT_API_KEY:
        africastalking.initialize(AT_USERNAME, AT_API_KEY)
        sms = africastalking.SMS
    else:
        logger.warning("Africa's Talking credentials not set — returning None.")
        sms = None
except Exception as e:
    logger.exception("Failed to initialize Africa's Talking: %s", e)
    sms = None


def send_sms(to_number: str, message: str):
    """
    Send an SMS using Africa's Talking.
    Ensures number starts with '+'. Returns simulated response if client not configured.
    """
    if not sms:
        logger.info(f"Simulating SMS send to {to_number}: {message}")
        return {"status": "simulated", "to": to_number, "message": message}

    # Ensure + prefix
    if not to_number.startswith("+"):
        to_number = f"+{to_number}"

    try:
        response = sms.send(message, [to_number])
        logger.info("SMS sent: %s", response)
        return response
    except Exception as e:
        logger.warning("Failed to send SMS, returning simulated response. Error: %s", e)
        return {"status": "simulated", "to": to_number, "message": message}
