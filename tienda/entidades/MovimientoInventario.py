from django.db import models

from tienda.entidades.identificadores import generar_id


class MovimientoInventario(models.Model):
    class Tipo(models.TextChoices):
        ENTRADA = "entrada", "Entrada"
        SALIDA = "salida", "Salida"
        AJUSTE = "ajuste", "Ajuste"

    idMovimientoInventario = models.CharField(
        primary_key=True,
        max_length=50,
        
    )
    varianteId = models.ForeignKey(
        "tienda.VarianteProducto",
        db_column="varianteId",
        on_delete=models.PROTECT,
        related_name="movimientos_inventario",
    )
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    motivo = models.CharField(max_length=100)
    pedidoId = models.ForeignKey(
        "tienda.Pedido",
        db_column="pedidoId",
        on_delete=models.SET_NULL,
        related_name="movimientos_inventario",
        null=True,
        blank=True,
    )
    usuarioId = models.ForeignKey(
        "tienda.Usuario",
        db_column="usuarioId",
        on_delete=models.SET_NULL,
        related_name="movimientos_inventario",
        null=True,
        blank=True,
    )
    observaciones = models.TextField()

    class Meta:
        app_label = "tienda"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(cantidad__gt=0),
                name="movimiento_cantidad_positiva",
            ),
        ]

    def __str__(self):
        return f"{self.tipo}: {self.varianteId.sku} ({self.cantidad})"
