from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField

from .articles import Category

from django.db.models import Q


class CustomUser(AbstractUser):
    email = models.EmailField(_("email address"), unique=True, )

    is_active = models.BooleanField(
        _("active"),
        default=False,
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


# Общий профиль
class Profile(models.Model):
    class TypeUser(models.IntegerChoices):
        CLIENT = 0, 'Пользователь'
        EXPERT = 1, 'Эксперт'

    avatar = models.ImageField('Аватар', upload_to="avatars", default="avatars/profile_picture_icon.png")
    type = models.IntegerField("Категория пользователя", choices=TypeUser.choices, default=TypeUser.CLIENT)
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='profile')


class ExpertManager(models.Manager):
    #
    def get_queryset(self):
        return super(ExpertManager, self).get_queryset().filter(
            Q(profile__type=Profile.TypeUser.EXPERT) & Q(expertprofile__status=ExpertProfile.ExpertStatus.VERIFIED) & Q(is_active=True))

# Сущность Эксперта
class Expert(CustomUser):
    objects = ExpertManager()

    class Meta:
        proxy = True


# Профиль эксперта
class ExpertProfile(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='expertprofile')

    about = models.CharField(max_length=2000, null=True)
    education = models.CharField(max_length=250, null=True)
    age = models.IntegerField(null=True)
    hour_cost = models.IntegerField(null=True)
    experience = models.IntegerField(null=True)

    class ExpertStatus(models.IntegerChoices):
        NOT_VERIFIED = 0, 'Неверифицирован'
        VERIFIED = 1, 'Верифицирован'

    status = models.IntegerField("Статус проверки Эксперта", choices=ExpertStatus.choices,
                                 default=ExpertStatus.NOT_VERIFIED)
    # rating = models.FloatField(null=True)
    # expert_categories = ArrayField(models.ForeignKey(Category, on_delete=models.CASCADE), size = 10)


# Создаем обработчик сигнала для добавления профиля при создании пользователя
# @receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()


class UserActivation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    activation_key = models.CharField(max_length=255)
    expiration_date = models.DateTimeField(default=timezone.now)

    def has_expired(self):
        return timezone.now() >= self.expiration_date
