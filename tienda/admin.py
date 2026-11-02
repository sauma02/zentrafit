
# tienda/admin.py
from django.contrib import admin
from .entidades import (
    Categoria, Producto, VarianteProducto, ImagenProducto, 
    Usuario, Pedido, DetallePedido, MovimientoInventario, Pago, Carrito
)

# Registramos todas las entidades para que aparezcan en el panel de control
admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(VarianteProducto)
admin.site.register(ImagenProducto)
admin.site.register(Usuario)
admin.site.register(Pedido)
admin.site.register(DetallePedido)
admin.site.register(MovimientoInventario)
admin.site.register(Pago)
admin.site.register(Carrito)

# Register your models here.
