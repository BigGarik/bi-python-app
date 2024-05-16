from django.test import TestCase

from web.models.users import UploadToPathAndRename

from web.services import ExpertRatingCalculation, ExpertEducationsRow, ExpertProfileRow


# Моки для имитации экземпляров моделей
class MockUser:
    def __init__(self, id):
        self.id = id


class MockExpertProfile:
    def __init__(self, user):
        self.user = user


class MockInstance:
    def __init__(self, expertprofile):
        self.expertprofile = expertprofile


class UploadToPathAndRenameTestCase(TestCase):
    def test_upload_to_path_and_rename(self):
        # Путь, который будет использоваться для сохранения файлов
        path = 'expert/documents'
        # Создаем экземпляр класса UploadToPathAndRename
        uploader = UploadToPathAndRename(path)

        # Создаем моки для экземпляров моделей
        user = MockUser(id=123)
        expertprofile = MockExpertProfile(user=user)
        instance = MockInstance(expertprofile=expertprofile)

        # Имя файла для тестирования
        filename = 'resume.pdf'

        # Вызываем метод __call__ и проверяем результат
        expected_path = f'expert/documents/123/{filename}'
        generated_path = uploader(instance, filename)

        # Проверяем, что путь сгенерирован корректно
        self.assertEqual(generated_path, expected_path)


class ExpertRatingCalculationTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Здесь вы можете создать тестовые данные в базе данных, если это необходимо
        pass

    def setUp(self):
        # Этот метод вызывается перед каждым тестовым методом
        self.calculator = ExpertRatingCalculation()

    def test_calculate_primary_education_rating(self):
        educations = [
            ExpertEducationsRow(
                education_type='primary',
                specialized_education=True,
                educational_institution='Test University',
                educational_institution_verified=True,
                diploma_number=123,
                diploma_number_verified=True
            ),
            # Добавьте больше экземпляров ExpertEducationsRow для тестирования различных сценариев
        ]
        rating = self.calculator._calculate_primary_education_rating(educations)
        print('primary_education_rating ', rating)
        self.assertEqual(rating, 2)  # Ожидаемое значение рейтинга

    def test_calculate_additional_education_rating(self):
        educations = [
            ExpertEducationsRow(
                education_type='additional',
                specialized_education=True,
                educational_institution='Test Course',
                educational_institution_verified=True,
                diploma_number=456,
                diploma_number_verified=False
            ),
            # Добавьте больше экземпляров ExpertEducationsRow для тестирования различных сценариев
        ]
        rating = self.calculator._calculate_additional_education_rating(educations)
        print('additional_education_rating ', rating)
        self.assertEqual(rating, 2)  # Ожидаемое значение рейтинга

    def test_calculate_consulting_experience_rating(self):
        profile = ExpertProfileRow(
            expert_categories=['Category1', 'Category2'],
            consulting_experience=5,
            experience=10,
            hh_link='http://example.com',
            linkedin_link='http://linkedin.com',
            is_verified=1
        )
        rating = self.calculator._calculate_consulting_experience_rating(profile)
        print('consulting_experience_rating ', rating)
        self.assertEqual(rating, 3)  # Ожидаемое значение рейтинга

    def test_calculate_experience_rating(self):
        profile = ExpertProfileRow(
            expert_categories=['Category1', 'Category2'],
            consulting_experience=2,
            experience=5,
            hh_link='http://example.com',
            linkedin_link='http://linkedin.com',
            is_verified=1
        )
        rating = self.calculator._calculate_experience_rating(profile)
        print('experience_rating ', rating)
        self.assertEqual(rating, 3)  # Ожидаемое значение рейтинга
