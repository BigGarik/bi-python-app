import logging

import pytz
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from django.db.models import Q

from web.models import Category


logger = logging.getLogger('django-debug')


phone_regex = RegexValidator(
    regex=r'^((8|\+374|\+994|\+995|\+375|\+7|\+380|\+38|\+996|\+998|\+993)[\- ]?)?\(?\d{3,5}\)?[\- ]?\d{1}[\- ]?\d{'
          r'1}[\- ]?\d{1}[\- ]?\d{1}[\- ]?\d{1}(([\- ]?\d{1})?[\- ]?\d{1})?$',
    message=_("Phone number must be entered in the format: '+79997654321'. Up to 15 digits allowed.")
)


@deconstructible
class UploadToPathAndRename(object):
    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        expert_id = instance.expertprofile.user.id
        return f'{self.sub_path}/{expert_id}/{filename}'


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

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse('user_profile', kwargs={'int': self.pk})


# Общий профиль
class Profile(models.Model):
    class TypeUser(models.IntegerChoices):
        CLIENT = 0, _('Client')
        EXPERT = 1, _('Expert')

    avatar = models.ImageField(verbose_name=_('Avatar'), upload_to="avatars",
                               default="avatars/profile_picture_icon.png")
    type = models.IntegerField(verbose_name=_('Category user'), choices=TypeUser.choices, default=TypeUser.CLIENT)
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='profile')

    # Новое поле для часового пояса
    timezone = models.CharField(
        max_length=50,
        choices=[(tz, tz) for tz in pytz.all_timezones],
        default='Europe/Moscow',
        verbose_name=_('Time Zone')
    )


class ExpertManager(models.Manager):
    #
    def get_queryset(self):
        return super(ExpertManager, self).get_queryset().filter(
            Q(profile__type=Profile.TypeUser.EXPERT) & Q(expertprofile__isnull=False) &
            Q(is_active=True))


# Сущность Эксперта
class Expert(CustomUser):
    objects = ExpertManager()

    class Meta:
        proxy = True


class BaseExpertProfile(models.Model):
    about = models.CharField(max_length=2000, null=True)
    age = models.IntegerField(null=True)
    hour_cost = models.IntegerField(null=True)  # Стоимость часа
    expert_categories = models.ManyToManyField(Category)
    education = models.ManyToManyField('Education')
    documents = models.ManyToManyField('Document')
    consulting_experience = models.IntegerField(default=0)  # Опыт консультирования
    """ Опыт работы """
    experience = models.IntegerField(default=0)
    hh_link = models.URLField(max_length=200, blank=True, verbose_name=_('Link to HH'))
    linkedin_link = models.URLField(max_length=200, blank=True, verbose_name=_('Link to LinkedIn'))
    points = models.IntegerField(default=0, blank=True, null=True, verbose_name=_("points"))

    class Meta:
        abstract = True


# Профиль эксперта
class ExpertProfile(BaseExpertProfile):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='expertprofile')

    rating = models.FloatField(null=True)


class ExpertAnketa(BaseExpertProfile):
    class AnketaVerifiedStatus(models.IntegerChoices):
        NOT_VERIFIED = 0, _('Unverified')
        VERIFIED = 1, _('Verified')

    is_verified = models.IntegerField(_("Expert verification status"), choices=AnketaVerifiedStatus.choices,
                                      default=AnketaVerifiedStatus.NOT_VERIFIED)

    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, null=False, related_name='expertanketa')

    def save(self, *args, **kwargs):
        logger.debug(f"Saving ExpertAnketa for user: {self.user.id if self.user else 'None'}")
        super().save(*args, **kwargs)


class Education(models.Model):
    """ Образование """
    EDUCATION_TYPE_CHOICES = (
        ('primary', _('Primary')),
        ('additional', _('Additional')),
    )
    #expert_profile = models.ForeignKey(ExpertProfile, on_delete=models.SET_NULL, null=True, related_name='educations')
    #expert_anketa = models.ForeignKey(ExpertAnketa, on_delete=models.SET_NULL, null=True, related_name='anketa_educations')
    education_type = models.CharField(max_length=10, choices=EDUCATION_TYPE_CHOICES, default='primary',
                                      verbose_name=_('Education Type'))
    specialized_education = models.BooleanField(default=False)  # Профильное или нет образование
    educational_institution = models.CharField(max_length=250, null=True, blank=True,
                                               verbose_name=_('Educational Institution'))
    diploma_number = models.IntegerField(null=True, blank=True,
                                         verbose_name=_('Educational Institution'))
    # degree_documents = models.ManyToManyField('Document', blank=True, related_name='degree_documents',
    # verbose_name=_('Education documents'))

    # def save(self, *args, **kwargs):
    #     # Если экземпляр уже существует в базе данных (не новый)
    #     if self.pk:
    #         # Получаем старый экземпляр из базы данных
    #         old_instance = Education.objects.get(pk=self.pk)
    #         # Проверяем, изменилось ли поле
    #         if old_instance.educational_institution != self.educational_institution:
    #             # Если изменилось, устанавливаем 'educational_institution_verified' в False
    #             self.educational_institution_verified = False
    #         if old_instance.diploma_number != self.diploma_number:
    #             # Если изменилось, устанавливаем 'diploma_number_verified' в False
    #             self.diploma_number_verified = False
    #     super().save(*args, **kwargs)


class Document(models.Model):
    file = models.FileField(upload_to=UploadToPathAndRename('expert/documents'), verbose_name=_('File'))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Date of upload'))
    # Добавьте ForeignKey для связи с ExpertProfile
    #expert_profile = models.ForeignKey(ExpertProfile, on_delete=models.SET_NULL, related_name='documents', null=True, blank=True)
    #expert_anketa =  models.ForeignKey(ExpertProfile, on_delete=models.SET_NULL, related_name='anketa_documents', null=True,  blank=True)

    # Добавляем ForeignKey для Education
    education = models.ForeignKey(Education, on_delete=models.CASCADE, related_name='degree_documents', null=True,
                                  blank=True)

    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')

    def get_absolute_url(self):
        return reverse('document_detail', kwargs={'pk': self.pk})


class Grade(models.Model):
    min_points = models.IntegerField(verbose_name=_("min_points"))
    max_points = models.IntegerField(verbose_name=_("max_points"))
    grade = models.CharField(max_length=50, verbose_name=_("grade"))
    min_cost = models.IntegerField(verbose_name=_("min_cost"))
    max_cost = models.IntegerField(null=True, blank=True, verbose_name=_("max_cost"))
    commission_size = models.IntegerField(verbose_name=_("commission_size"))
