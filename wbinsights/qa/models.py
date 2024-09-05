from django.contrib.contenttypes.models import ContentType
from django.db import models
from vote.models import VoteModel

from web.models import CustomUser, Category


class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(CustomUser, related_name='questions', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    targeted_user = models.ForeignKey(CustomUser, related_name='targeted_questions', on_delete=models.SET_NULL, null=True, blank=True)
    cat = models.ForeignKey(Category, related_name='questions', on_delete=models.PROTECT, verbose_name="Категории")

    def __str__(self):
        return self.title


class Answer(VoteModel, models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    content = models.TextField()
    author = models.ForeignKey(CustomUser, related_name='answers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_best = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['author', 'question'], name='unique_answer_per_user')
        ]

    def save(self, *args, **kwargs):
        if self.pk:  # Если объект уже существует (т.е. это редактирование)
            old_instance = Answer.objects.get(pk=self.pk)
            if old_instance.content != self.content:  # Если содержание изменилось
                # Получаем все голоса и удаляем их
                content_type = ContentType.objects.get_for_model(self)
                votes = self.votes.through.objects.filter(content_type=content_type, object_id=self.pk)
                votes.delete()
                # Сбрасываем счетчики голосов
                self.vote_score = 0
                self.num_vote_up = 0
                self.num_vote_down = 0
                self.is_best = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Answer by {self.author.username} to {self.question.title}"
