from django import forms
from django.core.validators import FileExtensionValidator

from .models import UserProject, UserProjectFile


class UserProjectForm(forms.ModelForm):
    key_results_text = forms.CharField(
        widget=forms.Textarea,
        help_text='Пожалуйста, введите каждый ключевой результат на новой строке.',
        required=False
    )

    class Meta:
        model = UserProject
        fields = ['name', 'category', 'customer', 'year', 'goals', 'key_results_text',]

    def __init__(self, *args, **kwargs):
        super(UserProjectForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            # Инициализация поля key_results_text данными из модели, если объект уже существует
            self.fields['key_results_text'].initial = '\n'.join(self.instance.key_results)

    def clean_key_results_text(self):
        # Получаем текст из формы, разбиваем по переводам строк и убираем пустые строки
        text = self.cleaned_data.get('key_results_text', '')
        key_results_list = [line.strip() for line in text.splitlines() if line.strip()]
        return key_results_list

    def save(self, commit=True):
        # Обычное сохранение, без коммита
        instance = super().save(commit=False)
        instance.key_results = self.cleaned_data.get('key_results_text', [])

        if commit:
            instance.save()
            self.save_m2m()
        return instance


class UserProjectEditForm(forms.ModelForm):
    class Meta:
        model = UserProject
        fields = ['name', 'category', 'customer', 'year', 'goals', 'key_results',]


class UserProjectFileForm(forms.ModelForm):
    file = forms.FileField(
        required=False,  # Указываем, что загрузка файла необязательна
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'odt', 'txt', 'xlsx', 'xls']
            )
        ],
        help_text='Разрешены только документы.'
    )

    class Meta:
        model = UserProjectFile
        fields = ['file']
