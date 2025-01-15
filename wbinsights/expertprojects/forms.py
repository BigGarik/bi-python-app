import datetime

from django import forms
from django.core.validators import FileExtensionValidator

from web.models import CustomUser, Category
from .models import UserProject, UserProjectFile, UserProjectCustomer


class UserProjectForm(forms.ModelForm):
    key_results_text = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control form-control-resize', 'rows': 6}),
        help_text='Пожалуйста, введите каждый ключевой результат на новой строке.',
        required=False
    )
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        label="Категории проекта",
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True
    )
    year = forms.IntegerField(
        initial=datetime.date.today().year,
        min_value=1985,
        max_value=datetime.date.today().year,
        label="Год проекта",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = UserProject
        fields = ['name', 'category', 'company', 'year', 'goals', 'key_results_text']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'goals': forms.Textarea(attrs={'class': 'form-control form-control-resize', 'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] += ' form-control'

        if self.instance.pk:
            self.fields['key_results_text'].initial = '\n'.join(self.instance.key_results)

        # Optionally, you can add placeholders here
        self.fields['name'].widget.attrs['placeholder'] = 'Введите название проекта'
        self.fields['company'].widget.attrs['placeholder'] = 'Введите название компании'

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
