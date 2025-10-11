import random
import redis
import os

class OTPSendError(Exception):
    pass

class OTPManager:
    def __init__(self) -> None:
        self.redis_client = redis.Redis(
            host = os.getenv('REDIS_HOST'),
            port = int(os.getenv('REDIS_PORT'))
            decode_responses=True
        )
        self.otp_expire = 6000
        self.sms_interval = 60
        self.sms_limit = 1

    def create_otp(self) -> str:
        return str(random.randint(1000, 9999))

    def can_send_sms(self, username) -> bool:
        key = f'sms_limit:{username}'
        data = self.redis_client.incr(key)
        if (data) == 1:
            self.redis_client.expire(key, self.sms_interval)
        if data > self.sms_limit:
            return False
        return True
        
    def save_otp(self, username, otp) -> None:
        if not self.can_send_sms(username):
            raise OTPSendError(f'Новую СМС можно получить через {self.redis_client.ttl(f"sms_limit:{username}")} сек.')
        self.redis_client.set(username, otp, ex=self.otp_expire)

    def get_otp(self, username) -> str:
        otp_code = self.redis_client.get(username)
        if not otp_code:
            raise OTPSendError(f'Получите новый код или проверьте данные.')
        return otp_code

    def delete_otp(self, username) -> None:
        self.redis_client.delete(username)

        