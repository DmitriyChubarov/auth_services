from celery import shared_task
from typing import Any, Dict
import requests
import os

class SMSSender:
    def __init__(self) -> None:
        self.api_key = os.getenv('SMS_API_KEY'),
        self.api_url = 'https://sms.ru/sms/send'
        self.sender = os.getenv('SMS_SENDER')
    
    def send_sms(self, phone_number, otp_code) -> Dict[str, Any]:
        payload = {
            "api_id": self.api_key,
            "to": phone_number,
            "msg": f"Ваш код для входа: {otp_code}",
            "json": 1
        }

        try:
            response = requests.post(self.api_url, data=payload, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"detail": str(e)}

@shared_task
def send_sms_task(phone_number, otp_code) -> Dict[str, Any]:
    sender = SMSSender()
    return  sender.send_sms(phone_number, otp_code)