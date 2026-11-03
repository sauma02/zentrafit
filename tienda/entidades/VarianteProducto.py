from django.db import models

from tienda.entidades.identificadores import generar_id


class VarianteProducto(models.Model):
    varianteId = models.CharField(
        primary_key=True,
        max_length=50,
        
    )
    idProducto = models.ForeignKey(
        "tienda.Producto",
        db_column="idProducto",
        on_delete=models.CASCADE,
        related_name="variantes",
    )
    sku = models.CharField(max_length=50, unique=True)
    sabor = models.CharField(max_length=50)
    tamano = models.CharField(max_length=50)
    unidadMedida = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)
    precio = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        app_label = "tienda"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(precio__gte=0),
                name="variante_precio_no_negativo",
            ),
        ]

    def __str__(self):
        return f"{self.sku} - {self.idProducto.nombre}"