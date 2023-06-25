from django.db import models

# Create your models here.


class Cal(models.Model):
    question = models.CharField(max_length=20)
    answer = models.CharField(max_length=20)
    count = models.FloatField(max_length=10)