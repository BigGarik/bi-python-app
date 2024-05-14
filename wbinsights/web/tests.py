from django.test import TestCase

from web.models.users import UploadToPathAndRename, CustomUser, ExpertProfile, Education, Document


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


class ExpertProfileRatingTestCase(TestCase):
    def setUp(self):
        # Создаем пользователя для связи с профилем эксперта
        self.user = CustomUser.objects.create(username='testuser')
        # Создаем экземпляр ExpertProfile для тестирования
        self.expert_profile = ExpertProfile.objects.create(
            user=self.user,
            experience=0,
            is_verified=ExpertProfile.ExpertVerifiedStatus.NOT_VERIFIED
        )
        # Создаем основное образование для эксперта
        self.primary_education = Education.objects.create(
            expert_profile=self.expert_profile,
            education_type='primary',
            specialized_education=True,
            educational_institution='Test University',
            diploma_number=123456,
            educational_institution_verified=False,
            diploma_number_verified=False
        )

    def test_calculate_experience_rating(self):
        # Тестирование расчета рейтинга опыта
        self.expert_profile.experience = 10
        self.assertEqual(self.expert_profile._calculate_experience_rating(), 3)

        self.expert_profile.experience = 5
        self.expert_profile.hh_link = 'http://example.com/hh'
        self.assertEqual(self.expert_profile._calculate_experience_rating(), 3)

        # Добавить дополнительные тесты для других сценариев

    def test_calculate_primary_education_rating(self):
        # Сценарий, когда учебное заведение и номер диплома верифицированы
        self.primary_education.educational_institution_verified = True
        self.primary_education.diploma_number_verified = True
        self.primary_education.save()
        self.assertEqual(self.expert_profile._calculate_primary_education_rating(), 2)

        # Сценарий, когда учебное заведение верифицировано, но номер диплома нет
        self.primary_education.diploma_number_verified = False
        self.primary_education.save()
        # Создаем и верифицируем документ об образовании
        verified_document = Document.objects.create(is_verified=True)
        self.primary_education.degree_documents.add(verified_document)
        self.assertEqual(self.expert_profile._calculate_primary_education_rating(), 2)

        # Сценарий, когда учебное заведение верифицировано, но нет верифицированных документов
        self.primary_education.degree_documents.clear()
        self.assertEqual(self.expert_profile._calculate_primary_education_rating(), 1)

        # Сценарий, когда учебное заведение не верифицировано
        self.primary_education.educational_institution_verified = False
        self.primary_education.save()
        self.assertEqual(self.expert_profile._calculate_primary_education_rating(), 0)

        # Добавить дополнительные тесты для других сценариев

    def test_calculate_rating(self):
        # Тестирование расчета среднего рейтинга
        self.expert_profile.experience = 10
        self.expert_profile.specialized_education = True
        self.expert_profile.educational_institution = 'University'
        self.expert_profile.number_diploma = '123456'
        self.expert_profile.is_verified = ExpertProfile.ExpertVerifiedStatus.VERIFIED
        self.expert_profile._calculate_rating()
        self.assertEqual(self.expert_profile.rating, 2.5)

        # Добавить дополнительные тесты для других сценариев
