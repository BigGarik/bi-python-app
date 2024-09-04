from django.db import models
from vote.models import VoteModel

from web.models import CustomUser


class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(CustomUser, related_name='questions', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    targeted_user = models.ForeignKey(CustomUser, related_name='targeted_questions', on_delete=models.SET_NULL, null=True,
                                      blank=True)

    def __str__(self):
        return self.title


class Answer(VoteModel, models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    content = models.TextField()
    author = models.ForeignKey(CustomUser, related_name='answers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_best = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer by {self.author.username} to {self.question.title}"
