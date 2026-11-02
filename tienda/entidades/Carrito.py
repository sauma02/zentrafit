from django.db import models

from tienda.entidades.identificadores import generar_id


class Carrito(models.Model):
    idCarrito = models.CharField(
        primary_key=True,
        max_length=50,
        default=generar_id,
    )
    usuarioId = models.ForeignKey(
        "tienda.Usuario",
        db_column="usuarioId",
        on_delete=models.SET_NULL,
        related_name="carritos",
        null=True,
        blank=True,
    )
    fechaCreacion = models.DateTimeField(auto_now_add=True)
    sesionId = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
    )
    actualizadoEn = models.DateTimeField(auto_now=True)
    varianteId = models.ForeignKey(
        "tienda.VarianteProducto",
        db_column="varianteId",
        on_delete=models.PROTECT,
        related_name="carritos",
    )
    cantidad = models.PositiveIntegerField()

    class Meta:
        app_label = "tienda"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(cantidad__gt=0),
                name="carrito_cantidad_positiva",
            ),
            models.CheckConstraint(
                condition=models.Q(usuarioId__isnull=False)
                | models.Q(sesionId__isnull=False),
                name="carrito_usuario_o_sesion",
            ),
        ]

    def __str__(self):
        return f"{self.varianteId.sku} x {self.cantidad}"