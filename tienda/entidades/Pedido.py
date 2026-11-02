from django.db import models

from tienda.entidades.identificadores import generar_id


class Pedido(models.Model):
    idPedido = models.CharField(
        primary_key=True,
        max_length=50,
        default=generar_id,
    )
    numeroPedido = models.CharField(max_length=50, unique=True)
    usuarioId = models.ForeignKey(
        "tienda.Usuario",
        db_column="usuarioId",
        on_delete=models.SET_NULL,
        related_name="pedidos",
        null=True,
        blank=True,
    )
    fechaPedido = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=False)
    nombreCliente = models.CharField(max_length=50)
    apellidoCliente = models.CharField(max_length=50)
    emailContacto = models.EmailField(max_length=254)
    telefonoContacto = models.CharField(max_length=50)
    direccionDeEntrega = models.CharField(max_length=255)
    ciudadEntrega = models.CharField(max_length=100)
    descuento = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
    )
    costoEnvio = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        app_label = "tienda"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(descuento__isnull=True)
                | models.Q(descuento__gte=0, descuento__lte=1),
                name="pedido_descuento_rango",
            ),
            models.CheckConstraint(
                condition=models.Q(costoEnvio__gte=0),
                name="pedido_envio_no_negativo",
            ),
            models.CheckConstraint(
                condition=models.Q(total__gte=0),
                name="pedido_total_no_negativo",
            ),
        ]

    def __str__(self):
        return self.numeroPedido