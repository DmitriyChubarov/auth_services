from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework.response import Response

from .models import User

class TestUserRegistration(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='test_user_register',
            password='test_password_register',
            phone_number='1234567890',
        )

    def base_user_registration(self, test_user_register, test_password_register, test_password_register_2, phone_number) -> Response:
        response = self.client.post('/api/register/', {
            'username': test_user_register,
            'password': test_password_register,
            'password2': test_password_register_2,
            'phone_number': phone_number,
        })
        return response

    def test_user_registration(self) -> None:
        response = self.base_user_registration('test_user_register-1', 'test_password_register-1', 'test_password_register-1', '1234567891')
        self.assertEqual(response.status_code, 201)

    def test_user_registration_with_existing_user(self) -> None:
        response = self.base_user_registration('test_user_register', 'test_password_register-1', 'test_password_register-1', '1234567891')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['username'][0], 'Пользователь с таким именем уже существует.')

    def test_user_registration_with_existing_phone_number(self) -> None:
        response = self.base_user_registration('test_user_register-1', 'test_password_register-1', 'test_password_register-1', '1234567890')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['phone_number'][0], 'Пользователь с таким номером уже существует.')

    def test_user_registration_with_different_passwords(self) -> None:
        response = self.base_user_registration('test_user_register-1', 'test_password_register-1', 'test_password_register-2', '1234567891')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'][0], 'Пароли не совпадают.')
    
    def test_user_registration_with_short_password(self) -> None:
        response = self.base_user_registration('test_user_register-1', 't-1', 't-1', '1234567891')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['non_field_errors'][0], 'This password is too short. It must contain at least 8 characters.')
        
    def test_user_registration_with_weak_password(self) -> None:
        response = self.base_user_registration('test_user_register-1', '12345678', '12345678', '1234567891')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['non_field_errors'][0], 'This password is too common.')
        self.assertEqual(response.data['non_field_errors'][1], 'This password is entirely numeric.')

class TestUserLogin(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='test_user_login',
            password='test_password_login',
            phone_number='1234567890',
        )

    def base_user_login(self, test_user_login, test_password_login) -> None:
        response = self.client.post('/api/login/', {
            'username_or_phone': test_user_login,
            'password': test_password_login
        })
        return response

    def test_user_login(self) -> None:
        response = self.base_user_login('test_user_login', 'test_password_login')
        self.assertEqual(response.status_code, 200)

    def test_user_login_invalid_name(self) -> None:
        response = self.base_user_login('none', 'test_password_login')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'][0], "Пользователь не существует, пройдите регистрацию.")

    def test_user_login_invalid_password(self) -> None:
        response = self.base_user_login('test_user_login', 'none')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'][0], "Введён неправильный пароль.")

    # @patch('users.serializers.send_sms_task.delay')
    # @patch('users.serializers.OTPManager')
    # def test_user_none_name(self, mock_otp_manager_class, mock_send_sms):
         