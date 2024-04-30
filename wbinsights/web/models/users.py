from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django.db.models import Q

from web.models import Category

phone_regex = RegexValidator(
    regex=r'^((8|\+374|\+994|\+995|\+375|\+7|\+380|\+38|\+996|\+998|\+993)[\- ]?)?\(?\d{3,5}\)?[\- ]?\d{1}[\- ]?\d{'
          r'1}[\- ]?\d{1}[\- ]?\d{1}[\- ]?\d{1}(([\- ]?\d{1})?[\- ]?\d{1})?$',
    message=_("Phone number must be entered in the format: '+79997654321'. Up to 15 digits allowed.")
)


class CustomUser(AbstractUser):
    email = models.EmailField(_("Email"), unique=True, )
    phone_number = models.CharField(
        _("Phone number"),
        # unique=True,
        validators=[phone_regex],
        max_length=17,
        blank=False,  # После миграции сделать 'False', чтобы сделать поле обязательным
    )
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
            Q(profile__type=Profile.TypeUser.EXPERT) & Q(
                expertprofile__is_verified=ExpertProfile.ExpertVerifiedStatus.VERIFIED) & Q(
                is_active=True))


# Сущность Эксперта
class Expert(CustomUser):
    objects = ExpertManager()

    class Meta:
        proxy = True


class NonVerifiedExpertManager(models.Manager):
    #
    def get_queryset(self):
        return super(NonVerifiedExpertManager, self).get_queryset().filter(
            Q(profile__type=Profile.TypeUser.EXPERT) & Q(
                expertprofile__is_verified=ExpertProfile.ExpertVerifiedStatus.NOT_VERIFIED) & Q(
                is_active=True))


class NonVerifiedExpert(CustomUser):
    objects = NonVerifiedExpertManager()

    class Meta:
        proxy = True

    def __str__(self):
        return self.last_name + ' ' + self.first_name


# Профиль эксперта
class ExpertProfile(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='expertprofile')

    about = models.CharField(max_length=2000, null=True)
    education = models.CharField(max_length=250, null=True)
    age = models.IntegerField(null=True)
    hour_cost = models.IntegerField(null=True)
    experience = models.IntegerField(null=True)

    class ExpertVerifiedStatus(models.IntegerChoices):
        NOT_VERIFIED = 0, 'Неверифицирован'
        VERIFIED = 1, 'Верифицирован'

    is_verified = models.IntegerField(_("Expert verification status"), choices=ExpertVerifiedStatus.choices,
                                      default=ExpertVerifiedStatus.NOT_VERIFIED)
    # rating = models.FloatField(null=True)
    expert_categories = models.ManyToManyField(Category)


# Создаем обработчик сигнала для добавления профиля при создании пользователя
# @receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
