from celery import shared_task
from typing import Any, Dict
import json
import requests
import os

class SMSSender:
    def __init__(self) -> None:
        self.api_key = os.getenv('SMS_API_KEY')
        self.api_url = "https://lcab.smsprofi.ru/json/v1.0/sms/send/text"
        self.sender = os.getenv('SMS_SENDER')
    
    def send_sms(self, phone_number, otp_code) -> Dict[str, Any]:

        headers = {
            "X-Token": self.api_key,
            "Content-Type": "application/json"
        }

        message = {
            "recipient": phone_number,
            "text": f"Код для входа в личный кабинет - {otp_code}",
            "source": "auth_service" 
        }

        validate_payload = {
            "messages": [message],
            "validate": True
        }

        try:
            response = requests.post(self.api_url, headers=headers, data=json.dumps(validate_payload), timeout=5)
            response.raise_for_status()
            print(f"Код для входа в личный кабинет - {otp_code}")
            return response.json()
        except requests.RequestException as e:
            return {"detail": str(e)}

@shared_task
def send_sms_task(phone_number, otp_code) -> Dict[str, Any]:
    sender = SMSSender()
    return sender.send_sms(phone_number, otp_code)