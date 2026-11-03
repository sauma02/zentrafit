from django.db import models

from tienda.entidades.identificadores import generar_id


class Categoria(models.Model):
    categoriaId = models.CharField(
        primary_key=True,
        max_length=50,
        
    )
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField()
    activa = models.BooleanField(default=True)

    class Meta:
        app_label = "tienda"

    def __str__(self):
        return self.nombre