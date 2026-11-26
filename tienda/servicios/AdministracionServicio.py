from decimal import Decimal

from tienda.entidades import Categoria, Pedido, Producto
from tienda.servicios.InventarioServicio import InventarioServicio
from tienda.servicios.ProductoServicio import ProductoServicio


class AdministracionServicio:
    """Consultas agregadas usadas por el dashboard administrativo."""

    @staticmethod
    def resumen():
        products = list(ProductoServicio.mostrarTodosLosProductos())
        variants = [variant for product in products for variant in product.variantes.all()]
        orders = list(Pedido.objects.prefetch_related("detalles").order_by("-fechaPedido")[:8])
        completed_revenue = sum((order.total for order in Pedido.objects.filter(estado=True)), Decimal("0"))
        low_stock = [
            {
                "product": variant.idProducto.nombre,
                "sku": variant.sku,
                "stock": InventarioServicio.calcularStock(variant),
            }
            for variant in variants
            if InventarioServicio.calcularStock(variant) <= 5
        ]
        return {
            "products": products,
            "variants": variants,
            "orders": orders,
            "categories": Categoria.objects.filter(activa=True).count(),
            "pending_orders": Pedido.objects.filter(estado=False).count(),
            "revenue": completed_revenue,
            "low_stock": low_stock,
        }

    @staticmethod
    def listarPedidos():
        return Pedido.objects.prefetch_related("detalles").order_by("-fechaPedido")

    @staticmethod
    def actualizarEstadoPedido(order_id, completed):
        order = Pedido.objects.get(idPedido=order_id)
        order.estado = bool(completed)
        order.save(update_fields=["estado"])
        return order
