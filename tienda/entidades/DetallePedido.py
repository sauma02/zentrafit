from django.db import models

from tienda.entidades.identificadores import generar_id


class DetallePedido(models.Model):
    idDetalle = models.CharField(
        primary_key=True,
        max_length=50,
        
    )
    idPedido = models.ForeignKey(
        "tienda.Pedido",
        db_column="idPedido",
        on_delete=models.CASCADE,
        related_name="detalles",
    )
    varianteId = models.ForeignKey(
        "tienda.VarianteProducto",
        db_column="varianteId",
        on_delete=models.PROTECT,
        related_name="detalles_pedido",
    )
    nombreProducto = models.CharField(max_length=100)
    sku = models.CharField(max_length=50)
    cantidad = models.PositiveIntegerField()
    precioUnitario = models.DecimalField(max_digits=12, decimal_places=2)
    subTotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        app_label = "tienda"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(cantidad__gt=0),
                name="detalle_cantidad_positiva",
            ),
            models.CheckConstraint(
                condition=models.Q(precioUnitario__gte=0),
                name="detalle_precio_no_negativo",
            ),
            models.CheckConstraint(
                condition=models.Q(subTotal__gte=0),
                name="detalle_subtotal_no_negativo",
            ),
        ]

    def __str__(self):
        return f"{self.idPedido.numeroPedido} - {self.nombreProducto}"