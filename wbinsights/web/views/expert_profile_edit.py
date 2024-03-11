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
        
    firstname = forms.CharField(label="Имя", widget=forms.TextInput(attrs={'class': '123'}))
    lastname = forms.CharField(label="Фамилия", widget=forms.TextInput(attrs={'class': '123'}))
    about_me = forms.CharField(label="О себе", widget=forms.TextInput(attrs={'class': '123'}))
    #photo = forms.CharField(label="Фото", widget=forms.ImageField(attrs={'class': '123'}))
    category = forms.CharField(label="Категории экспертности", widget=forms.TextInput(attrs={'class': '123'}))
    experience = forms.IntegerField(label="Опыт работы (лет)", widget=forms.TextInput(attrs={'class': '123'}))
    rate = forms.IntegerField(label="Стоимость консультации (₽ за час)", widget=forms.TextInput(attrs={'class': '123'}))
                                    
    oldpassword = forms.CharField(label="Старый пароль", widget=forms.PasswordInput(attrs={'class': '123'}))
    newpassword = forms.CharField(label="Новый пароль", widget=forms.PasswordInput(attrs={'class': '123'}))
    confirmpassword = forms.CharField(label="Повторите новый пароль", widget=forms.PasswordInput(attrs={'class': '123'}))


class ProfileEditView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "posts/expert/expert_profile_edit.html"
