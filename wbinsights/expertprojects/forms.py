from django import forms
from expertprojects.models import UserProject


class UserProjectForm(forms.ModelForm):
    class Meta:
        model = UserProject
        fields = ['member', 'name', 'key_results', 'customer', 'year', 'category', 'goals']
