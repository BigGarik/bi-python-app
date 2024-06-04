from django import forms


class ExpertAnketaForm(forms.Form):
    id = forms.IntegerField()
    # user = forms.IntegerField()
    expert_categories = forms.CharField()
    educations = forms.CharField()
    documents = forms.CharField()
    about = forms.CharField()
    age = forms.IntegerField()
    hour_cost = forms.IntegerField()
    consulting_experience = forms.IntegerField()
    experience = forms.IntegerField()
    hh_link = forms.URLField()
    linkedin_link = forms.URLField()
    is_verified = forms.BooleanField()
    rating = forms.FloatField()

