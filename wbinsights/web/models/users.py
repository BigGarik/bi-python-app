from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    email = models.EmailField(_("email address"), unique=True,)

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    # profile = models.OneToOneField('Profile', on_delete=models.CASCADE, related_name='user', null=True, blank=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse('user_profile', kwargs={'int': self.pk})


class Profile(models.Model):

    class TypeUser(models.IntegerChoices):
        USER = 0, 'Пользователь'
        EXPERT = 1, 'Эксперт'

    avatar = models.ImageField('Аватар', upload_to="avatars", default="avatars/profile_picture_icon.png")
    type = models.BooleanField("Категория пользователя", choices=TypeUser.choices, default=TypeUser.USER)
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='profile')


# Создаем обработчик сигнала для добавления профиля при создании пользователя
@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
