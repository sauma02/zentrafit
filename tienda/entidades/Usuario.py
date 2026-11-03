from django.db import models

from tienda.entidades.identificadores import generar_id


class Usuario(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=50,
        
    )
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    password = models.CharField(max_length=128)
    edad = models.PositiveSmallIntegerField()
    correo = models.EmailField(max_length=254)
    esAdmin = models.BooleanField(default=False)
    esStaff = models.BooleanField(default=False)
    contacto = models.CharField(max_length=50)

    class Meta:
        app_label = "tienda"

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
