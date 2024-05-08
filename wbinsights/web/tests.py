from django.test import TestCase

from web.models.users import UploadToPathAndRename


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
