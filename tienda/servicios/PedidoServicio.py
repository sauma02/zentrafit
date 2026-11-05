from tienda.entidades.Pedido import Pedido
from tienda.entidades.Carrito import Carrito
from tienda.entidades.VarianteProducto import VarianteProducto
from tienda.entidades.identificadores import generar_id
from tienda.servicios.ProductoServicio import ProductoServicio
from tienda.entidades.DetallePedido import DetallePedido
from tienda.servicios.CarritoServicio import CarritoServicio
from datetime import datetime as Date
from tienda.entidades.MovimientoInventario import MovimientoInventario
from django.db import transaction 
from django.db import IntegrityError, DataError, OperationalError
from django.core.exceptions import (
    NON_FIELD_ERRORS,
    FieldDoesNotExist,
    FieldError,
    MultipleObjectsReturned,
    ObjectDoesNotExist,
    ObjectNotUpdated,
    ValidationError,
)

from tienda.entidades import Pago

class PedidoServicio():

    @transaction.atomic
    @staticmethod
    def crearPedido(usuario, carrito, datosCliente, direccion ,ciudad ,metodoPago, descuento):
        try:
            subTotal= sum(item.varianteId.precio*item.cantidad for item in carrito)
            costoEnvio=18000

            if not carrito.exists():
                raise ValidationError("El carrito esta vacio, no se puede crear el pedido")
            idCombinado = f"PD##{generar_id()}"
            if usuario == None:
                pedido=Pedido(idPedido=idCombinado,usuarioId=usuario, numeroPedido=f"NMPD##{generar_id()}", fechaPedido=Date.now(), estado=False,
                              nombreCLiente=datosCliente['nombre'], apellidoCliente=datosCliente['apellido'], emailContacto=datosCliente['email'], 
                              telefonoContacto=datosCliente['telefono'], direccionDeEntrega=direccion, ciudadEntrega=ciudad, descuento=descuento, 
                              costoEnvio=costoEnvio, total=(subTotal + costoEnvio-(subTotal*descuento)))
                pedido.full_clean()
                if pedido.full_clean() is None:
                    raise ValidationError("El pedido no es valido, no se puede crear, por favor verifique los datos ingresados")
                pedido.save()
                return pedido
            
            pedido=Pedido(idPedido=idCombinado,usuarioId=usuario, numeroPedido=f"NMPD##{generar_id()}", fechaPedido=Date.now(), estado=False,
                                          nombreCLiente=datosCliente['nombre'], apellidoCliente=datosCliente['apellido'], emailContacto=datosCliente['email'], 
                                          telefonoContacto=datosCliente['telefono'], direccionDeEntrega=direccion, ciudadEntrega=ciudad, descuento=descuento, 
                                          costoEnvio=costoEnvio, total=(subTotal + costoEnvio-(subTotal*descuento)))
            pedido.full_clean()
            if pedido.full_clean() is None:
                raise ValidationError("El pedido no es valido, no se puede crear, por favor verifique los datos ingresados")
            pedido.save()
            for index, item in enumerate(carrito):
                idDetalle=f"DTP##{generar_id()}"
                subTotalItem=item.varianteId.precio*item.cantidad
                varianteProducto=ProductoServicio.listarVarianteEspecifica(item.varianteId.varianteId)
                if not varianteProducto.exists():
                    raise ValidationError("La variante de producto no existe")
                if item.cantidad > varianteProducto.first().stock:
                    raise ValidationError(f"No hay suficiente stock para la variante {varianteProducto.first().sku}")
                detallePedido=DetallePedido(idDetalle=idDetalle, idPedido=pedido, varianteId=item.varianteId, 
                                            nombreProducto=item.varianteId.productoId.nombreProducto, sku= item.varianteId.sku,
                                            cantidad=item.cantidad, precioUnitario=item.varianteId.precio, subTotal=subTotalItem)

                detallePedido.full_clean()
                detallePedido.save()

                movimiento=MovimientoInventario(
                    idMovimientoInventario=f"MV##{generar_id()}",
                    varianteId=varianteProducto.first(),
                    tipo="Salida",
                    cantidad=item.cantidad,
                    fecha=Date.now(),
                    pedidoId=pedido,
                    usuarioId=usuario,
                    oberservaciones=f"Salidad de inventario por pedido {pedido.numeroPedido}"
                )
                movimiento.full_clean()
                if movimiento.full_clean() is None:
                    raise ValidationError("El movimiento de inventario no es valido, no se puede crear, por favor verifique los datos ingresados")
                movimiento.save()
                varianteProducto.first().stock -= item.cantidad
                varianteProducto.first().save()

                idPago=f"PG##{generar_id()}"
                pago=Pago(idPago=idPago, pedidoId=pedido, metodo=metodoPago, estado="Pendiente",
                           monto=pedido.total, referencia=f"REF##{generar_id()}", 
                           fechaPago=Date.now(), observacion="Pago por pedido, pendiente de pago")
                pago.full_clean()
                if pago.full_clean() is None:
                    raise ValidationError("El pago no es valido, no se puede crear, por favor verifique los datos ingresados")
                pago.save()
            carrito.delete()
            return pedido
        except ValidationError as e:
            print(f"Error critico, uno o mas campos estan vacios: {e}")
        except IntegrityError as e:
            print(f"Error fatal(Crear pedido): {e}")
      