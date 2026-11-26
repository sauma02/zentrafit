from django.core.exceptions import ValidationError
from django.db import transaction

from tienda.entidades import MovimientoInventario
from tienda.entidades.identificadores import generar_id
from tienda.servicios.ProductoServicio import ProductoServicio


class InventarioServicio:
    """Reglas de negocio para existencias y movimientos de inventario."""

    @staticmethod
    def calcularStock(variante):
        movimientos = MovimientoInventario.objects.filter(varianteId=variante)
        return sum(
            movement.cantidad if movement.tipo in {"entrada", "ajuste"} else -movement.cantidad
            for movement in movimientos
        )

    @staticmethod
    def listarVariantesConStock():
        return ProductoServicio.listaVariantes().order_by("sku")

    @staticmethod
    @transaction.atomic
    def registrarMovimiento(varianteId, tipo, cantidad, motivo="Ajuste administrativo", observaciones=""):
        if tipo not in {"entrada", "salida", "ajuste"}:
            raise ValidationError("El tipo de movimiento no es válido.")
        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError) as error:
            raise ValidationError("La cantidad debe ser un entero.") from error
        if cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")
        variante = ProductoServicio.listarVarianteEspecifica(varianteId)
        movimiento = MovimientoInventario(
            idMovimientoInventario=f"MOV##{generar_id()}",
            varianteId=variante,
            tipo=tipo,
            cantidad=cantidad,
            motivo=str(motivo or "Ajuste administrativo")[:100],
            observaciones=str(observaciones or ""),
        )
        movimiento.full_clean()
        movimiento.save()
        return movimiento
