from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from hitcount.models import HitCountMixin, HitCount
from vote.models import VoteModel

from web.models import Category
from django_comments_xtd.moderation import moderator, SpamModerator
from web.badwords import badwords
from web.utils import remove_scripts


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=Article.Status.PUBLISHED)


# теги
# class Post(models.Model):
#     name = models.CharField(max_length=200)
#     tags = ArrayField(models.CharField(max_length=200), blank=True)

#     def __str__(self):
#         return self.name
# contains¶
# The contains lookup is overridden on ArrayField. The returned objects will be those where the values passed are a subset of the data. It uses the SQL operator @>. For example:

# >>> Post.objects.create(name="First post", tags=["thoughts", "django"])
# >>> Post.objects.create(name="Second post", tags=["thoughts"])
# >>> Post.objects.create(name="Third post", tags=["tutorial", "django"])


class Article(VoteModel, models.Model, HitCountMixin):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    title = models.CharField(max_length=255, verbose_name="Заголовок")
    description = models.CharField(blank=True, verbose_name="Краткое описание")
    main_img = models.ImageField(upload_to='articles/%Y/%m', verbose_name='Главная картинка')
    content = models.TextField(blank=True, verbose_name="Текст статьи")
    author = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, related_name="article")
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(choices=Status.choices, default=Status.DRAFT, verbose_name="Статус")
    cat = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='article', verbose_name="Категории", )
    allow_comments = models.BooleanField('allow comments', default=True)
    styles = models.TextField(null=True, blank=True, verbose_name="Стили")
    hit_count_generic = GenericRelation(HitCount, object_id_field='object_pk',
                                        related_query_name='hit_count_generic_relation')

    objects = models.Manager()
    published = PublishedManager()

    def save(self, *args, **kwargs):
        # Удаляем <script> перед сохранением
        self.content = remove_scripts(self.content)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create'])
        ]

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})


class ArticleCommentModerator(SpamModerator):
    email_notification = True

    def moderate(self, comment, content_object, request):
        # Make a dictionary where the keys are the words of the message
        # and the values are their relative position in the message.
        def clean(word):
            ret = word
            if word.startswith('.') or word.startswith(','):
                ret = word[1:]
            if word.endswith('.') or word.endswith(','):
                ret = word[:-1]
            return ret

        lowcase_comment = comment.comment.lower()
        msg = dict([
            (clean(w), i)
            for i, w in enumerate(lowcase_comment.split())
        ])

        for badword in badwords:
            if isinstance(badword, str):
                if lowcase_comment.find(badword) > -1:
                    return True
            else:
                lastindex = -1
                for subword in badword:
                    if subword in msg:
                        if lastindex > -1:
                            if msg[subword] == (lastindex + 1):
                                lastindex = msg[subword]
                        else:
                            lastindex = msg[subword]
                    else:
                        break
                if msg.get(badword[-1]) and msg[badword[-1]] == lastindex:
                    return True

        return super(ArticleCommentModerator, self).moderate(
            comment, content_object, request
        )


moderator.register(Article, ArticleCommentModerator)