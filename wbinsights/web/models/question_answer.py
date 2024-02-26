from django.db import models
from django.urls import reverse


class QuestionAnswer(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def get_absolute_url(self):
        return reverse('question_answer_detail', kwargs={'slug': self.slug})
