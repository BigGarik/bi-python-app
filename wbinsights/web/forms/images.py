from django import forms
from ..models.models import Image


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']
