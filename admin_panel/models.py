from django.db import models
from django.utils.timezone import datetime

# Create your models here.

class Process(models.Model):
    process_name = models.CharField(max_length=32,blank=False, null=False, default=None, verbose_name='Название процесса')
    time_start = models.DateTimeField(blank=False, null=False, default=datetime.now(), verbose_name='Начало')
    time_end = models.DateTimeField(blank=True, null=False, default=datetime.now(), verbose_name='Конец')
    executable = models.BooleanField(blank=True, null=False, default=True, verbose_name='Выполняется')