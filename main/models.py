from django.db import models


class Alumno(models.Model):
    nombres = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    rut = models.CharField(max_length=12)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre + " " + self.apellido
