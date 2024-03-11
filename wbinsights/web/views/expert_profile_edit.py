from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy

from web.models import CustomUser
from django import forms


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")



class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("firstname", "lastname", "about_me", "category", "experience", "rate", "oldpassword", "newpassword", "confirmpassword") #photo
        
    firstname = forms.CharField(label="Имя", widget=forms.TextInput(attrs={'class': 'custom-form-css'}))
    lastname = forms.CharField(label="Фамилия", widget=forms.TextInput(attrs={'class': 'custom-form-css'}))
    about_me = forms.CharField(label="О себе", widget=forms.Textarea(attrs={'class': 'custom-aboutme-form'}))
    #photo = forms.CharField(label="Фото", widget=forms.ImageField(attrs={'class': '123'}))
    
    category = forms.CharField(label="Категории экспертности", widget=forms.TextInput(attrs={'class': 'custom-form-css'}))
    experience = forms.IntegerField(label="Опыт работы (лет)", widget=forms.TextInput(attrs={'class': 'custom-form-css'}))
    rate = forms.IntegerField(label="Стоимость консультации (₽ за час)", widget=forms.TextInput(attrs={'class': 'custom-form-css'}))
                                    
    oldpassword = forms.CharField(label="Старый пароль", widget=forms.PasswordInput(attrs={'class': 'custom-form-css'}))
    newpassword = forms.CharField(label="Новый пароль", widget=forms.PasswordInput(attrs={'class': 'custom-form-css'}))
    confirmpassword = forms.CharField(label="Повторите новый пароль", widget=forms.PasswordInput(attrs={'class': 'custom-form-css'}))


class ProfileEditView(CreateView):
    form_class = CustomUserChangeForm
    success_url = reverse_lazy("login")
    template_name = "posts/expert/expert_profile_edit.html"
