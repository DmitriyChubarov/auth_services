from django.test import TestCase

from rest_framework.test import APITestCase
from rest_framework.response import Response

from unittest.mock import patch, MagicMock

from .models import User

from users.serializers import OTPSendError

class BaseTestUser(APITestCase):
    """Базовый класс для тестов"""

    FIRST_VALID_PHONE = '88888888888'
    SECOND_VALID_PHONE = '87777777777'

    FIRST_VALID_PASSWORD = 'first_test_password'
    SECOND_VALID_PASSWORD = 'second_test_password'

    FIRST_VALID_USERNAME = 'first_test_username'
    SECOND_VALID_USERNAME = 'second_test_username'

    VALID_SMS = '0000'
    INVALID_SMS = '1111'

    INVALID_PHONE = '77777777777'
    INVALID_NAME = 'invalid_test_username'
    FIRST_INVALID_PASSWORD = 'in'
    SECOND_INVALID_PASSWORD = '12345678'

    NULL_FIELD = 'This field may not be blank.'

    OTP_PATCH = 'users.serializers.OTPManager'
    OTP_TASK = 'users.serializers.send_sms_task.delay'

    def create_user(self) -> User:
        return User.objects.create_user(
            username=self.FIRST_VALID_USERNAME,
            password=self.FIRST_VALID_PASSWORD,
            phone_number=self.FIRST_VALID_PHONE,
        )

class TestUserRegistration(BaseTestUser):
    """Класс для тестирования регистрации"""

    def setUp(self) -> None:
        self.user = self.create_user()

    def base_user_registration(self, test_user_register: str, test_password_register: str, test_password_register_2: str, phone_number: str) -> Response:
        response = self.client.post('/api/register/', {
            'username': test_user_register,
            'password': test_password_register,
            'password2': test_password_register_2,
            'phone_number': phone_number,
        })
        return response

    def test_user_registration(self) -> None:
        response = self.base_user_registration(self.SECOND_VALID_USERNAME, self.SECOND_VALID_PASSWORD, self.SECOND_VALID_PASSWORD, self.SECOND_VALID_PHONE)
        self.assertEqual(response.status_code, 201)

    def test_user_registration_with_existing_user(self) -> None:
        response = self.base_user_registration(self.FIRST_VALID_USERNAME, self.SECOND_VALID_PASSWORD, self.SECOND_VALID_PASSWORD, self.SECOND_VALID_PHONE)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['username'][0], 'Пользователь с таким именем уже существует.')

    def test_user_registration_with_existing_phone_number(self) -> None:
        response = self.base_user_registration(self.SECOND_VALID_USERNAME, self.SECOND_VALID_PASSWORD, self.SECOND_VALID_PASSWORD, self.FIRST_VALID_PHONE)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['phone_number'][0], 'Пользователь с таким номером уже существует.')

    def test_user_registration_with_different_passwords(self) -> None:
        response = self.base_user_registration(self.SECOND_VALID_USERNAME, self.FIRST_VALID_PASSWORD, self.SECOND_VALID_PASSWORD, self.SECOND_VALID_PHONE)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'][0], 'Пароли не совпадают.')

    def test_user_registration_with_invalid_phone_number(self) -> None:
        response = self.base_user_registration(self.SECOND_VALID_USERNAME, self.SECOND_VALID_PASSWORD, self.SECOND_VALID_PASSWORD, self.INVALID_PHONE)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'][0], 'Введен некорректный номер телефона. Формат: 8XXXXXXXXXX')
    
    def test_user_registration_with_short_password(self) -> None:
        response = self.base_user_registration(self.SECOND_VALID_USERNAME, self.FIRST_INVALID_PASSWORD, self.FIRST_INVALID_PASSWORD, self.SECOND_VALID_PHONE)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['non_field_errors'][0], 'This password is too short. It must contain at least 8 characters.')
        
    def test_user_registration_with_weak_password(self) -> None:
        response = self.base_user_registration(self.SECOND_VALID_USERNAME, self.SECOND_INVALID_PASSWORD, self.SECOND_INVALID_PASSWORD, self.SECOND_VALID_PHONE)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['non_field_errors'][0], 'This password is too common.')
        self.assertEqual(response.data['non_field_errors'][1], 'This password is entirely numeric.')

    def test_user_registration_null(self) -> None:
        response = self.base_user_registration('', '', '', '')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['username'][0], self.NULL_FIELD)
        self.assertEqual(response.data['password'][0], self.NULL_FIELD)
        self.assertEqual(response.data['password2'][0], self.NULL_FIELD)
        self.assertEqual(response.data['phone_number'][0], self.NULL_FIELD)

class TestUserLogin(BaseTestUser):
    """Класс для тестирования авторизации"""

    def setUp(self) -> None:
        self.user = self.create_user()

        patcher_otp = patch(self.OTP_PATCH)
        patcher_tasks = patch(self.OTP_TASK)
        self.mock_otp_manager_class = patcher_otp.start()
        self.addCleanup(patcher_otp.stop)

        self.mock_otp_manager = MagicMock()
        self.mock_otp_manager_class.return_value = self.mock_otp_manager

        self.mock_otp_manager.create_otp.return_value = '123456'
        self.mock_otp_manager.save_otp.return_value = None

        self.send_sms_task = patcher_tasks.start()
        self.addCleanup(patcher_tasks.stop)

        self.send_sms_task.return_value = {'detail': '200'}


    def base_user_login(self, test_user_login: str, test_password_login: str) -> Response:
        response = self.client.post('/api/login/', {
            'username_or_phone': test_user_login,
            'password': test_password_login
        })
        return response

    def test_user_login(self) -> None:
        response = self.base_user_login(self.FIRST_VALID_USERNAME, self.FIRST_VALID_PASSWORD)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['detail'], "Код отправлен на телефон")
    
    def test_user_login_repeat(self) -> None:
        self.mock_otp_manager.save_otp.side_effect = [True, OTPSendError('Новый код можно получить через 59 сек.')]
        response_first = self.base_user_login(self.FIRST_VALID_USERNAME, self.FIRST_VALID_PASSWORD)
        response_second = self.base_user_login(self.FIRST_VALID_USERNAME, self.FIRST_VALID_PASSWORD)
        self.assertEqual(response_second.status_code, 400)
        self.assertIn("Новый код можно получить", response_second.data['detail'][0])

    def test_user_login_invalid_name(self) -> None:
        response = self.base_user_login(self.INVALID_NAME, self.FIRST_VALID_PASSWORD)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'][0], "Пользователь не существует, пройдите регистрацию.")

    def test_user_login_invalid_password(self) -> None:
        response = self.base_user_login(self.FIRST_VALID_USERNAME, self.FIRST_INVALID_PASSWORD)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'][0], "Введён неправильный пароль.") 

    def test_user_login_null(self) -> None:
        response = self.base_user_login('', '')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['username_or_phone'][0], self.NULL_FIELD)
        self.assertEqual(response.data['password'][0], self.NULL_FIELD)

class TestUserSMS(BaseTestUser):
    """Класс для тестирования отправки смс кода"""

    def setUp(self) -> None:
        self.user = self.create_user()
    
        patcher = patch(self.OTP_PATCH)
        self.mock_otp_manager_class = patcher.start()
        self.addCleanup(patcher.stop)

        self.mock_otp_manager = MagicMock()
        self.mock_otp_manager_class.return_value = self.mock_otp_manager

        self.mock_otp_manager.get_otp.return_value = '0000'
        self.mock_otp_manager.delete_otp.return_value = None


    def base_user_sms(self, username: str, otp: str):
        response = self.client.post('/api/sms/',{
            'username_or_phone': username,
            'sms_code': otp
        })

        return response

    def test_user_sms(self) -> None:
        response = self.base_user_sms(self.FIRST_VALID_USERNAME, self.VALID_SMS)
        self.assertEqual(response.status_code, 200)   
        self.assertEqual(response.data['detail'], 'Успешная авторизация')   
        self.assertIsInstance(response.data['access_token'], str)
        self.assertIsInstance(response.data['refresh_token'], str)

    def test_user_invalid_sms(self) -> None:
        response = self.base_user_sms(self.FIRST_VALID_USERNAME, self.INVALID_SMS)
        self.assertEqual(response.status_code, 400)   
        self.assertEqual(response.data['detail'][0], 'Введён неверный код.') 

    def test_user_expired_sms(self) -> None:
        self.mock_otp_manager.get_otp.side_effect = OTPSendError('Получите новый код или проверьте данные.')
        
        response = self.base_user_sms(self.FIRST_VALID_USERNAME, self.VALID_SMS)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'][0], 'Получите новый код или проверьте данные.')

    def test_user_invalid_username(self) -> None:
        response = self.base_user_sms(self.SECOND_VALID_USERNAME, self.VALID_SMS)
        self.assertEqual(response.status_code, 400)   
        self.assertEqual(response.data['detail'][0], 'Не удалось найти данные пользователя. Попробуйте войти заново.') 

    def test_user_sms_null(self) -> None:
        response = self.base_user_sms('', '')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['username_or_phone'][0], self.NULL_FIELD)
        self.assertEqual(response.data['sms_code'][0], self.NULL_FIELD)

          