from django import forms
from django.core.validators import FileExtensionValidator
from django.forms import SelectMultiple

from web.models import CustomUser, Category
from .models import UserProject, UserProjectFile


class UserProjectForm(forms.ModelForm):
    key_results_text = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control form-control-resize', 'rows': 4}),
        help_text='Пожалуйста, введите каждый ключевой результат на новой строке.',
        required=False
    )

    members = forms.ModelMultipleChoiceField(label="Members", queryset=CustomUser.objects.all()[:0])
    category = forms.ModelMultipleChoiceField(label="Категории проекта", queryset=Category.objects.all())

    class Meta:

        model = UserProject
        fields = ['name', 'category', 'customer', 'year', 'goals', 'key_results_text', 'members']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'goals': forms.Textarea(attrs={'class': 'form-control form-control-resize', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super(UserProjectForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['key_results_text'].initial = '\n'.join(self.instance.key_results)

    def clean_key_results_text(self):
        text = self.cleaned_data.get('key_results_text', '')
        return [line.strip() for line in text.splitlines() if line.strip()]

    def save(self, commit=True):
        instance = super(UserProjectForm, self).save(commit=False)
        instance.key_results = self.cleaned_data.get('key_results_text', [])
        if commit:
            instance.save()
            self.save_m2m()
        return instance


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
