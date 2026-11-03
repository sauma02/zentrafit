from django.db import models

from tienda.entidades.identificadores import generar_id


class ImagenProducto(models.Model):
    idImagen = models.CharField(
        primary_key=True,
        max_length=50,
        
    )
    idProducto = models.ForeignKey(
        "tienda.Producto",
        db_column="idProducto",
        on_delete=models.CASCADE,
        related_name="imagenes",
    )
    archivo = models.CharField(max_length=255)
    esPrincipal = models.BooleanField(default=False)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        app_label = "tienda"
        ordering = ["orden", "idImagen"]

    def __str__(self):
        return f"Imagen {self.idImagen} de {self.idProducto.nombre}"