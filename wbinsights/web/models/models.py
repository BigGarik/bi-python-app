from django.db import models


class Image(models.Model):
    image = models.ImageField(upload_to='images/%Y/%m/%d/')
    article = models.ForeignKey('Article', related_name='image', on_delete=models.CASCADE)

    def __str__(self):
        return f"Image for {self.article}"



    


