

from django.shortcuts import render, redirect
from django.contrib import messages
from tienda.servicios.CarritoServicio import CarritoServicio
from tienda.servicios.PedidoServicio import PedidoServicio
from tienda.servicios.ProductoServicio import ProductoServicio
from tienda.servicios.UsuarioServicio import UsuarioServicio
from tienda.entidades.VarianteProducto import VarianteProducto

def vistaCatalogo(request):

    productos=ProductoServicio.mostrarCatalogo()
    variantes=ProductoServicio.listaVariantes().filter(activo=True)
    carrito=CarritoServicio.listarCarrito(request.session.session_key)
    if carrito is None:
        carrito=[]
        contexto={
            "productos":productos,
            "variantes":variantes,
            "carrito":carrito,
            "titulo_pagina":"Catalogo de productos"
        }
    else:
        contexto={
                "productos":productos,
                "variantes":variantes,
                "carrito":carrito,
                "titulo_pagina":"Catalogo de productos"
                }    
    return render(request, "tienda/catalogo.html", contexto)
def agregarAlCarritoVista(request, varianteId):
    usuarioId=None
    if not request.session.session_key:
        request.session.create()
    sesionId=request.session.session_key
    try:
        carrito= CarritoServicio.agregarItem(usuarioId, varianteId, 1, sesionId)
        messages.success(request, "Producto agregado al carrito")
        return redirect(vistaCatalogo)
    except Exception as e:
        messages.error(request, f"Error al agregar al carrito: {str(e)}")
    
# Create your views here.
