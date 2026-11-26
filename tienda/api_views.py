import json
import re
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from tienda.entidades import Carrito, DetallePedido, Pago, Pedido, Producto, VarianteProducto
from tienda.servicios.CarritoServicio import CarritoServicio
from tienda.servicios.PedidoServicio import PedidoServicio
from tienda.servicios.ProductoServicio import ProductoServicio


def _origin(request):
    return request.headers.get("Origin") or ""


def _is_allowed_origin(origin):
    return bool(
        origin
        and (
            origin.endswith(".manus.computer")
            or origin.endswith(".app.github.dev")
            or re.match(r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$", origin)
        )
    )


def _response(request, payload, status=200):
    response = JsonResponse(payload, status=status)
    origin = _origin(request)
    if _is_allowed_origin(origin):
        response["Access-Control-Allow-Origin"] = origin
        response["Access-Control-Allow-Credentials"] = "true"
        response["Vary"] = "Origin"
    return response


def _options(request):
    response = _response(request, {})
    response["Access-Control-Allow-Methods"] = "GET, POST, PATCH, DELETE, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Accept, Content-Type, X-CSRFToken"
    return response


def _session_id(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def _money(value):
    return float(value or 0)


def _serialize_variant(variant):
    return {
        "id": variant.varianteId,
        "sku": variant.sku,
        "flavor": variant.sabor,
        "size": variant.tamano,
        "unit": variant.unidadMedida,
        "price": _money(variant.precio),
        "active": variant.activo,
    }


def _serialize_product(request, product):
    images = list(product.imagenes.all())
    primary = next((image for image in images if image.esPrincipal), images[0] if images else None)
    image_urls = [
        request.build_absolute_uri(image.archivo.url)
        for image in images
        if image.archivo
    ]
    return {
        "id": product.idProducto,
        "name": product.nombre,
        "description": product.descripcion,
        "brand": product.marca,
        "category": product.categoriaId.nombre,
        "imageUrl": request.build_absolute_uri(primary.archivo.url) if primary and primary.archivo else None,
        "images": image_urls,
        "variants": [_serialize_variant(variant) for variant in product.variantes.filter(activo=True)],
    }


def _serialize_cart(cart_items):
    lines = []
    total = Decimal("0")
    for item in cart_items:
        variant = item.varianteId
        product = variant.idProducto
        line_total = variant.precio * item.cantidad
        total += line_total
        lines.append({
            "id": item.idCarrito,
            "variantId": variant.varianteId,
            "productId": product.idProducto,
            "name": product.nombre,
            "brand": product.marca,
            "sku": variant.sku,
            "flavor": variant.sabor,
            "size": variant.tamano,
            "unit": variant.unidadMedida,
            "price": _money(variant.precio),
            "quantity": item.cantidad,
            "lineTotal": _money(line_total),
        })
    return {"lines": lines, "total": _money(total), "count": sum(line["quantity"] for line in lines)}


@ensure_csrf_cookie
@require_http_methods(["GET", "OPTIONS"])
def csrf_token(request):
    if request.method == "OPTIONS":
        return _options(request)
    return _response(request, {"detail": "CSRF cookie ready", "csrfToken": get_token(request)})


@require_http_methods(["GET", "OPTIONS"])
def catalog_api(request):
    if request.method == "OPTIONS":
        return _options(request)
    products = ProductoServicio.mostrarCatalogo()
    return _response(request, {"products": [_serialize_product(request, product) for product in products]})


@require_http_methods(["GET", "POST", "PATCH", "DELETE", "OPTIONS"])
def cart_api(request):
    if request.method == "OPTIONS":
        return _options(request)
    session_id = _session_id(request)
    if request.method == "GET":
        items = CarritoServicio.obtenerCarrito(session_id)
        return _response(request, _serialize_cart(items))

    if request.method == "DELETE":
        try:
            data = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return _response(request, {"detail": "JSON inválido."}, 400)
        variant_id = data.get("variantId")
        CarritoServicio.eliminarItem(session_id, variant_id)
        items = CarritoServicio.obtenerCarrito(session_id)
        return _response(request, _serialize_cart(items))

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return _response(request, {"detail": "JSON inválido."}, 400)

    variant_id = data.get("variantId")
    if not variant_id:
        return _response(request, {"detail": "variantId es obligatorio."}, 400)
    try:
        quantity = int(data.get("quantity", 1))
        if request.method == "PATCH":
            CarritoServicio.actualizarItem(session_id, variant_id, quantity)
        else:
            CarritoServicio.agregarItem(None, variant_id, quantity, session_id)
    except (ValidationError, VarianteProducto.DoesNotExist) as error:
        detail = error.messages[0] if isinstance(error, ValidationError) else "La variante no existe o está inactiva."
        return _response(request, {"detail": detail}, 400 if isinstance(error, ValidationError) else 404)
    items = CarritoServicio.obtenerCarrito(session_id)
    return _response(request, _serialize_cart(items), 201 if request.method == "POST" else 200)


@csrf_protect
@require_http_methods(["POST", "OPTIONS"])
def order_api(request):
    if request.method == "OPTIONS":
        return _options(request)
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return _response(request, {"detail": "JSON inválido."}, 400)

    required = ["name", "lastName", "email", "phone", "address", "city"]
    missing = [field for field in required if not str(data.get(field, "")).strip()]
    if missing:
        return _response(request, {"detail": "Faltan campos obligatorios.", "fields": missing}, 400)

    session_id = _session_id(request)
    try:
        discount = Decimal(str(data.get("discount", "0")))
    except InvalidOperation:
        return _response(request, {"detail": "El descuento no es válido."}, 400)
    try:
        order = PedidoServicio.crearPedidoDesdeSesion(
            sesionId=session_id,
            datosCliente=data,
            metodoPago=data.get("paymentMethod", "Pendiente"),
            descuento=discount,
        )
    except ValidationError as error:
        return _response(request, {"detail": error.messages[0]}, 400)

    return _response(request, {"orderId": order.idPedido, "orderNumber": order.numeroPedido, "total": _money(order.total)}, 201)
