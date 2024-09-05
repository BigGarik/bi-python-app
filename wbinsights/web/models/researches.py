from django.db import models
from django.urls import reverse


class Research(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def get_absolute_url(self):
        return reverse('research_detail', kwargs={'slug': self.slug})
