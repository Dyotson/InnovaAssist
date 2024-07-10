from django.db import models


class Alumno(models.Model):
    code = models.CharField(max_length=50)
    count = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
