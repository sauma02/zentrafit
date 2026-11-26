from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from tienda.entidades import DetallePedido, Pago, Pedido
from tienda.entidades.identificadores import generar_id
from tienda.servicios.CarritoServicio import CarritoServicio


class PedidoServicio:
    """Reglas de negocio para creación y gestión de pedidos."""

    @staticmethod
    @transaction.atomic
    def crearPedido(usuario, carrito, datosCliente, direccion, ciudad, metodoPago, descuento=Decimal("0")):
        carrito = carrito if hasattr(carrito, "exists") else list(carrito)
        if not carrito.exists() if hasattr(carrito, "exists") else not carrito:
            raise ValidationError("El carrito está vacío, no se puede crear el pedido.")
        descuento = Decimal(str(descuento or "0"))
        if descuento < 0 or descuento > 1:
            raise ValidationError("El descuento debe estar entre 0 y 1.")
        subtotal = sum((item.varianteId.precio * item.cantidad for item in carrito), Decimal("0"))
        costo_envio = Decimal("18000")
        pedido = Pedido(
            idPedido=f"PD##{generar_id()}",
            usuarioId=usuario,
            numeroPedido=f"NMPD##{generar_id()}",
            estado=False,
            nombreCliente=str(datosCliente["nombre"]).strip(),
            apellidoCliente=str(datosCliente["apellido"]).strip(),
            emailContacto=str(datosCliente["email"]).strip(),
            telefonoContacto=str(datosCliente["telefono"]).strip(),
            direccionDeEntrega=str(direccion).strip(),
            ciudadEntrega=str(ciudad).strip(),
            descuento=descuento,
            costoEnvio=costo_envio,
            total=subtotal + costo_envio - (subtotal * descuento),
        )
        pedido.full_clean()
        pedido.save()
        for item in carrito:
            DetallePedido.objects.create(
                idDetalle=f"DTP##{generar_id()}",
                idPedido=pedido,
                varianteId=item.varianteId,
                nombreProducto=item.varianteId.idProducto.nombre,
                sku=item.varianteId.sku,
                cantidad=item.cantidad,
                precioUnitario=item.varianteId.precio,
                subTotal=item.varianteId.precio * item.cantidad,
            )
        Pago.objects.create(
            idPago=f"PG##{generar_id()}",
            pedidoId=pedido,
            metodo=str(metodoPago or "Pendiente"),
            estado="Pendiente",
            monto=pedido.total,
            referencia=f"REF##{generar_id()}",
            fechaPago=timezone.now(),
            observaciones="Pago pendiente de confirmación.",
        )
        return pedido

    @staticmethod
    @transaction.atomic
    def crearPedidoDesdeSesion(sesionId, datosCliente, metodoPago="Pendiente", descuento=Decimal("0"), usuario=None):
        carrito = CarritoServicio.obtenerCarrito(sesionId)
        if not carrito.exists():
            raise ValidationError("El carrito está vacío.")
        pedido = PedidoServicio.crearPedido(
            usuario=usuario,
            carrito=carrito,
            datosCliente={
                "nombre": datosCliente["name"],
                "apellido": datosCliente["lastName"],
                "email": datosCliente["email"],
                "telefono": datosCliente["phone"],
            },
            direccion=datosCliente["address"],
            ciudad=datosCliente["city"],
            metodoPago=metodoPago,
            descuento=descuento,
        )
        CarritoServicio.eliminarItem(sesionId)
        return pedido
