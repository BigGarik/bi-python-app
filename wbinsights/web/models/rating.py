from django.db import models

from web.models import CustomUser


class RatingRole(models.Model):
    name = models.CharField(max_length=255, unique=True)
    text = models.TextField()


class RatingCalculate(models.Model):
    role = models.ForeignKey(RatingRole, related_name='role', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, related_name='user', on_delete=models.CASCADE)
    score = models.IntegerField(verbose_name='score')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['role', 'user'], name='unique_role_user')
        ]
