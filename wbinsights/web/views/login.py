from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.http import HttpResponse


from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy

from django import forms

from web.models import CustomUser, Profile






class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")



#Кастомный класс обработчик авторизации
class WBILoginView(LoginView):

    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('index')

    def form_invalid(self, form):
        messages.error(self.request, 'Неправильный логин или пароль')
        return self.render_to_response(self.get_context_data(form=form))

    #template_name = "users/login.html"
    
    pass

#Форма регистрации пользователя
class CustomUserCreationForm(UserCreationForm):

    
    # username = forms.CharField(label="ФИО", widget=forms.TextInput(attrs={'class': '123'}))
    # email    = forms.CharField(label="емаил", widget=forms.EmailInput(attrs={'class': '123'}))
    # phone_number = forms.RegexField(label="телефон", widget=forms.TextInput(attrs={'class': '123'}), 
    #                                 regex="^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$")
    # password1 = forms.CharField(label="p1", widget=forms.PasswordInput(attrs={'class': '123'}))
    # password2 = forms.CharField(label="p2", widget=forms.PasswordInput(attrs={'class': '123'}))

    user_type = forms.ChoiceField(choices= Profile.TypeUser, widget=forms.RadioSelect(attrs={'class':'4444'})) 
       
    #phone_number = forms.RegexField(regex="^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$")
    def save(self):
        print("123")
        #instance = super(CustomUserCreationForm, self).save()

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "email")
        #fields = ("user_type", "username", "email", "phone_number", "password1", "password2")


class WBIRegisterUser(CreateView):

    #create CustomUser

    #if (user_type == 'Expert')

    #we have to Create ExpertProfile
    #send email

    #else

    #send activation link
    

   # def form
    
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


    # def form_valid(self, form: CustomUserCreationForm) -> HttpResponse:

    #     # form.user_type
    #     return super().form_valid(form)
