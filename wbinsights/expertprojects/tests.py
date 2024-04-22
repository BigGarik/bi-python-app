from django.test import TestCase
from django.urls import reverse
from web.models import CustomUser, Profile


class SearchExpertsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаем экспертов для тестирования
        expert1 = CustomUser.objects.create_user(
            username='expert1',
            first_name='expert1',
            email='expert1@example.com',
            password='12345',
            phone_number='1234567890'
        )
        Profile.objects.create(user=expert1, type=Profile.TypeUser.EXPERT)

        expert2 = CustomUser.objects.create_user(
            username='expert2',
            first_name='expert2',
            email='expert2@example.com',
            password='12345',
            phone_number='0987654321'
        )
        Profile.objects.create(user=expert2, type=Profile.TypeUser.EXPERT)

        # Создаем пользователя, который не является экспертом
        user = CustomUser.objects.create_user(
            username='user',
            first_name='user',
            email='user@example.com',
            password='12345',
            phone_number='1122334455'
        )
        Profile.objects.create(user=user, type=Profile.TypeUser.CLIENT)

    def test_search_experts_ajax(self):
        # URL для представления search_experts
        url = reverse('search_experts')
        # Отправляем AJAX запрос с параметром term
        response = self.client.get(
            url,
            {'term': 'expert'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        # Проверяем, что в ответе содержатся данные обоих экспертов
        self.assertContains(response, 'expert1')
        self.assertContains(response, 'expert2')
        # Проверяем, что данные обычного пользователя не возвращаются
        self.assertNotContains(response, 'user')
