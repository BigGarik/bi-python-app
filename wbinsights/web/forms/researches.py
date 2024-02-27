from django import forms
from web.models import Research


class ResearchForm(forms.ModelForm):
    class Meta:
        model = Research
        fields = ['name']
