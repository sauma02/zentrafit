from django.test import TestCase
from django.utils import timezone

from tienda.entidades import (
    Carrito,
    Categoria,
    DetallePedido,
    ImagenProducto,
    MovimientoInventario,
    Pago,
    Pedido,
    Producto,
    Usuario,
    VarianteProducto,
)


class EntidadesRelacionTests(TestCase):
    def test_entidades_guardan_y_exponen_sus_relaciones(self):
        usuario = Usuario.objects.create(
            nombre="Ana",
            apellido="Pérez",
            password="hash",
            edad=30,
            correo="ana@example.com",
            contacto="3001234567",
        )
        categoria = Categoria.objects.create(
            nombre="Proteínas",
            descripcion="Suplementos de proteína",
        )
        producto = Producto.objects.create(
            categoriaId=categoria,
            nombre="Proteína Whey",
            descripcion="Proteína sabor vainilla",
            marca="ZentraFit",
        )
        variante = VarianteProducto.objects.create(
            idProducto=producto,
            sku="WHEY-VAINILLA-1KG",
            sabor="Vainilla",
            tamano="1 kg",
            unidadMedida="kg",
            precio="90000.00",
        )
        imagen = ImagenProducto.objects.create(
            idProducto=producto,
            archivo="imagenes/proteina.jpg",
            esPrincipal=True,
        )
        pedido = Pedido.objects.create(
            numeroPedido="PED-1001",
            usuarioId=usuario,
            nombreCliente="Ana",
            apellidoCliente="Pérez",
            emailContacto="ana@example.com",
            telefonoContacto="3001234567",
            direccionDeEntrega="Calle 1 # 2-3",
            ciudadEntrega="Bogotá",
            costoEnvio="5000.00",
            total="95000.00",
        )
        detalle = DetallePedido.objects.create(
            idPedido=pedido,
            varianteId=variante,
            nombreProducto=producto.nombre,
            sku=variante.sku,
            cantidad=1,
            precioUnitario="90000.00",
            subTotal="90000.00",
        )
        pago = Pago.objects.create(
            pedidoId=pedido,
            metodo="Transferencia",
            estado="confirmado",
            monto="95000.00",
            referencia="TRX-1001",
            fechaPago=timezone.now(),
            observaciones="Pago confirmado",
        )
        movimiento = MovimientoInventario.objects.create(
            varianteId=variante,
            tipo=MovimientoInventario.Tipo.SALIDA,
            cantidad=1,
            motivo="Venta",
            pedidoId=pedido,
            usuarioId=usuario,
            observaciones="Salida por pedido",
        )
        carrito = Carrito.objects.create(
            usuarioId=usuario,
            varianteId=variante,
            cantidad=2,
        )

        self.assertEqual(producto.categoriaId, categoria)
        self.assertEqual(categoria.productos.get(), producto)
        self.assertEqual(variante.idProducto, producto)
        self.assertEqual(producto.imagenes.get(), imagen)
        self.assertEqual(pedido.detalles.get(), detalle)
        self.assertEqual(pedido.pagos.get(), pago)
        self.assertEqual(variante.movimientos_inventario.get(), movimiento)
        self.assertEqual(usuario.carritos.get(), carrito)
        self.assertTrue(pedido.usuarioId)
        self.assertTrue(usuario.pk)

    def test_pedido_y_carrito_admiten_compra_de_invitado(self):
        categoria = Categoria.objects.create(
            nombre="Creatinas",
            descripcion="Suplementos de creatina",
        )
        producto = Producto.objects.create(
            categoriaId=categoria,
            nombre="Creatina",
            descripcion="Creatina monohidratada",
            marca="ZentraFit",
        )
        variante = VarianteProducto.objects.create(
            idProducto=producto,
            sku="CREA-300G",
            sabor="Sin sabor",
            tamano="300 g",
            unidadMedida="g",
            precio="45000.00",
        )
        pedido = Pedido.objects.create(
            numeroPedido="PED-1002",
            nombreCliente="Luis",
            apellidoCliente="Díaz",
            emailContacto="luis@example.com",
            telefonoContacto="3009876543",
            direccionDeEntrega="Carrera 4 # 5-6",
            ciudadEntrega="Medellín",
            costoEnvio="0.00",
            total="45000.00",
        )
        carrito = Carrito.objects.create(
            sesionId="sesion-invitado-1002",
            varianteId=variante,
            cantidad=1,
        )

        self.assertIsNone(pedido.usuarioId)
        self.assertIsNone(carrito.usuarioId)
        self.assertEqual(carrito.sesionId, "sesion-invitado-1002")
