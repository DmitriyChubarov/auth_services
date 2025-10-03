import random
import redis
import os

class OTPManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host = os.getenv('REDIS_HOST'),
            port = int(os.getenv('REDIS_PORT'))
        )
    
    def create_otp(self) -> str:
        return str(random.randint(1000, 9999))

    def save_otp(self, username, otp):
        self.redis_client.set(username, otp, ex=120)
        