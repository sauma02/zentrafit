from django.core.exceptions import ValidationError
from django.db import transaction

from tienda.entidades import Carrito
from tienda.entidades.identificadores import generar_id
from tienda.servicios.ProductoServicio import ProductoServicio


class CarritoServicio:
    """Reglas de negocio del carrito por usuario o sesión."""

    @staticmethod
    def obtenerCarrito(sesionId):
        if not sesionId:
            raise ValidationError("Se requiere un ID de sesión para listar el carrito.")
        return Carrito.objects.filter(sesionId=sesionId).select_related("varianteId", "varianteId__idProducto")

    @staticmethod
    def listarCarrito(sesionId):
        if not sesionId:
            return None
        carrito = CarritoServicio.obtenerCarrito(sesionId)
        return carrito if carrito.exists() else None

    @staticmethod
    @transaction.atomic
    def agregarItem(usuarioId, varianteId, cantidad, sesionId=None):
        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError) as error:
            raise ValidationError("La cantidad debe ser un entero.") from error
        if cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")
        variante = ProductoServicio.listarVarianteEspecifica(varianteId)
        usuario = None
        if usuarioId:
            raise ValidationError("El carrito autenticado requiere el servicio de usuarios.")
        if not sesionId:
            raise ValidationError("Se requiere un ID de sesión para usuarios no autenticados.")
        item = Carrito.objects.filter(usuarioId=usuario, sesionId=sesionId, varianteId=variante).first()
        if item:
            item.cantidad += cantidad
            item.save(update_fields=["cantidad", "actualizadoEn"])
            return item
        return Carrito.objects.create(
            idCarrito=f"CRT##{generar_id()}",
            usuarioId=usuario,
            sesionId=sesionId,
            varianteId=variante,
            cantidad=cantidad,
        )

    @staticmethod
    @transaction.atomic
    def actualizarItem(sesionId, varianteId, cantidad):
        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError) as error:
            raise ValidationError("La cantidad debe ser un entero.") from error
        if cantidad < 1:
            return CarritoServicio.eliminarItem(sesionId, varianteId)
        item = Carrito.objects.get(sesionId=sesionId, varianteId_id=varianteId)
        item.cantidad = cantidad
        item.save(update_fields=["cantidad", "actualizadoEn"])
        return item

    @staticmethod
    @transaction.atomic
    def eliminarItem(sesionId, varianteId=None):
        queryset = Carrito.objects.filter(sesionId=sesionId)
        if varianteId:
            queryset = queryset.filter(varianteId_id=varianteId)
        queryset.delete()
        return True
