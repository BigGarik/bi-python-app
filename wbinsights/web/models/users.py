from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from django.db.models import Q

from web.models import Category

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
        CLIENT = 0, _('Client')
        EXPERT = 1, _('Expert')

    avatar = models.ImageField(verbose_name=_('Avatar'), upload_to="avatars",
                               default="avatars/profile_picture_icon.png")
    type = models.IntegerField(verbose_name=_('Category user'), choices=TypeUser.choices, default=TypeUser.CLIENT)
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
    age = models.IntegerField(null=True)
    hour_cost = models.IntegerField(null=True)  # Стоимость часа
    expert_categories = models.ManyToManyField(Category)  # Категории экспертности
    consulting_experience = models.IntegerField(default=0)  # Опыт консультирования
    """ Опыт работы """
    experience = models.IntegerField(default=0)
    hh_link = models.URLField(max_length=200, blank=True, verbose_name=_('Link to HH'))
    linkedin_link = models.URLField(max_length=200, blank=True, verbose_name=_('Link to LinkedIn'))
    experience_documents = models.ManyToManyField('Document', blank=True, related_name='experience_documents',
                                                  verbose_name=_('Documents confirming experience'))

    """ Верификация """

    class ExpertVerifiedStatus(models.IntegerChoices):
        NOT_VERIFIED = 0, _('Unverified')
        VERIFIED = 1, _('Verified')

    is_verified = models.IntegerField(_("Expert verification status"), choices=ExpertVerifiedStatus.choices,
                                      default=ExpertVerifiedStatus.NOT_VERIFIED)

    rating = models.FloatField(null=True)

    def _calculate_experience_rating(self):
        # Проверяем наличие ссылок или документов
        has_links_or_documents = self.hh_link or self.linkedin_link or self.experience_documents.exists()

        if self.experience >= 10:
            return 3
        elif self.experience >= 5 and has_links_or_documents:
            return 3
        elif self.experience >= 5:
            return 2
        elif self.experience >= 2 and has_links_or_documents:
            return 2
        elif self.experience >= 3:
            return 1
        elif self.experience >= 2 and has_links_or_documents:
            return 1
        else:
            return 0

    def _calculate_primary_education_rating(self):
        # Получаем основное образование эксперта
        primary_education = self.educations.filter(education_type='primary').first()

        # Если основное образование существует и является профильным
        if primary_education and primary_education.specialized_education:
            # Проверяем заполненность учебного заведения и статус верификации
            if primary_education.educational_institution_verified:
                # Проверяем заполненность номера диплома и статус верификации
                if primary_education.diploma_number_verified:
                    return 2
                # Проверяем наличие верифицированных документов об образовании
                elif primary_education.degree_documents.filter(is_verified=True).exists():
                    return 2
                else:
                    return 1
        # В ином случае присваиваем значение 0
        return 0

    def _calculate_consulting_experience_rating(self):
        # Проверяем наличие ссылок или документов
        has_links_or_documents = self.hh_link or self.linkedin_link or self.experience_documents.exists()

        if self.consulting_experience >= 5:
            return 3
        elif self.consulting_experience >= 3 and has_links_or_documents:
            return 3
        elif self.consulting_experience >= 3:
            return 2
        elif self.consulting_experience >= 2 and has_links_or_documents:
            return 2
        else:
            return 0

    def _calculate_additional_education_rating(self):
        # Получаем все дополнительные образования эксперта, которые являются профильными
        additional_educations = self.educations.filter(education_type='additional', specialized_education=True)
        # Инициализируем рейтинг
        rating = 0
        # Перебираем все дополнительные образования
        for education in additional_educations:
            # Проверяем, верифицировано ли учебное заведение
            if education.educational_institution_verified:
                # Проверяем, есть ли верифицированные документы об образовании
                if education.degree_documents.filter(is_verified=True).exists():
                    # Присваиваем балл 2
                    rating += 2
                else:
                    # Присваиваем балл 1
                    rating += 1
        # Возвращаем итоговый рейтинг
        return rating

    def _calculate_rating(self):
        ratings = [
            self._calculate_primary_education_rating(),
            self._calculate_experience_rating(),
            self._calculate_consulting_experience_rating(),
            self._calculate_additional_education_rating(),
            # Добавить сюда вызовы других методов расчета рейтинга по мере их создания
        ]
        self.rating = sum(ratings) if ratings else 0


class Education(models.Model):
    """ Образование """
    EDUCATION_TYPE_CHOICES = (
        ('primary', _('Primary')),
        ('additional', _('Additional')),
    )
    expert_profile = models.ForeignKey(ExpertProfile, on_delete=models.CASCADE, related_name='educations')
    education_type = models.CharField(max_length=10, choices=EDUCATION_TYPE_CHOICES, default='primary',
                                      verbose_name=_('Education Type'))
    specialized_education = models.BooleanField(default=False)  # Профильное или нет образование
    educational_institution = models.CharField(max_length=250, null=True, blank=True,
                                               verbose_name=_('Educational Institution'))
    educational_institution_verified = models.BooleanField(default=False)
    diploma_number = models.IntegerField(null=True, blank=True,
                                         verbose_name=_('Educational Institution'))
    diploma_number_verified = models.BooleanField(default=False)
    degree_documents = models.ManyToManyField('Document', blank=True, related_name='degree_documents',
                                              verbose_name=_('Education documents'))


class Document(models.Model):
    file = models.FileField(upload_to=UploadToPathAndRename('expert/documents'), verbose_name=_('File'))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Date of upload'))
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')

    def get_absolute_url(self):
        return reverse('document_detail', kwargs={'pk': self.pk})


# Создаем обработчик сигнала для добавления профиля при создании пользователя
# @receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
