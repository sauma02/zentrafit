from django.db import models

from tienda.entidades.identificadores import generar_id


class Producto(models.Model):
    idProducto = models.CharField(
        primary_key=True,
        max_length=50,
        default=generar_id,
    )
    categoriaId = models.ForeignKey(
        "tienda.Categoria",
        db_column="categoriaId",
        on_delete=models.PROTECT,
        related_name="productos",
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    marca = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)
    fechaCreacion = models.DateField(auto_now_add=True)

    class Meta:
        app_label = "tienda"

    def __str__(self):
        return self.nombre
