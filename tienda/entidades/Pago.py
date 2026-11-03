from django.db import models

from tienda.entidades.identificadores import generar_id


class Pago(models.Model):
    idPago = models.CharField(
        primary_key=True,
        max_length=50,
        
    )
    pedidoId = models.ForeignKey(
        "tienda.Pedido",
        db_column="pedidoId",
        on_delete=models.CASCADE,
        related_name="pagos",
    )
    metodo = models.CharField(max_length=50)
    estado = models.CharField(max_length=30)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    referencia = models.CharField(max_length=100)
    fechaPago = models.DateTimeField()
    observaciones = models.TextField()

    class Meta:
        app_label = "tienda"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(monto__gte=0),
                name="pago_monto_no_negativo",
            ),
        ]

    def __str__(self):
        return f"{self.idPago} - {self.estado}"