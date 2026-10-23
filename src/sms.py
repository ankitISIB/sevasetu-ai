import os
import requests


SMSLOCAL_API = "https://app.smslocal.in/api"


def send_test_sms(phone_number, message, sender_id, template_id):
    """
    Send one approved test SMS through SMSLocal.
    """

    api_key = os.getenv("SMSLOCAL_KEY")

    if not api_key:
        return {
            "success": False,
            "message": "SMSLOCAL_KEY is not available in this terminal session."
        }

    params = {
        "key": api_key,
        "route": 1,
        "sender": sender_id,
        "number": phone_number,
        "sms": message,
        "templateid": template_id,
    }

    try:

        response = requests.get(
            f"{SMSLOCAL_API}/smsapi",
            params=params,
            timeout=20,
        )

        result = response.text.strip()

        if response.status_code == 200 and result.isdigit():

            return {
                "success": True,
                "message_id": result,
                "message": "SMS submitted successfully."
            }

        return {
            "success": False,
            "message": f"SMSLocal response: {result}"
        }

    except Exception as e:

        return {
            "success": False,
            "message": f"SMS request failed: {e}"
        }
