import json
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from django.db import transaction
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from tienda.entidades import Carrito, DetallePedido, Pago, Pedido, Producto, VarianteProducto


def _origin(request):
    return request.headers.get("Origin") or ""


def _response(request, payload, status=200):
    response = JsonResponse(payload, status=status)
    origin = _origin(request)
    if (
        origin in {"http://localhost:3000", "http://127.0.0.1:3000"}
        or origin.endswith(".manus.computer")
        or origin.endswith(".app.github.dev")
    ):
        response["Access-Control-Allow-Origin"] = origin
        response["Access-Control-Allow-Credentials"] = "true"
        response["Vary"] = "Origin"
    return response


def _options(request):
    response = _response(request, {})
    response["Access-Control-Allow-Methods"] = "GET, POST, PATCH, DELETE, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
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


def _serialize_product(product):
    images = list(product.imagenes.all())
    primary = next((image for image in images if image.esPrincipal), images[0] if images else None)
    return {
        "id": product.idProducto,
        "name": product.nombre,
        "description": product.descripcion,
        "brand": product.marca,
        "category": product.categoriaId.nombre,
        "imageUrl": primary.archivo if primary else None,
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
    products = Producto.objects.filter(activo=True).select_related("categoriaId").prefetch_related("variantes", "imagenes")
    return _response(request, {"products": [_serialize_product(product) for product in products]})


@require_http_methods(["GET", "POST", "PATCH", "DELETE", "OPTIONS"])
def cart_api(request):
    if request.method == "OPTIONS":
        return _options(request)
    session_id = _session_id(request)
    if request.method == "GET":
        items = Carrito.objects.filter(sesionId=session_id).select_related("varianteId", "varianteId__idProducto")
        return _response(request, _serialize_cart(items))

    if request.method == "DELETE":
        try:
            data = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return _response(request, {"detail": "JSON inválido."}, 400)
        variant_id = data.get("variantId")
        queryset = Carrito.objects.filter(sesionId=session_id)
        if variant_id:
            queryset = queryset.filter(varianteId_id=variant_id)
        queryset.delete()
        items = Carrito.objects.filter(sesionId=session_id).select_related("varianteId", "varianteId__idProducto")
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
    except (TypeError, ValueError):
        return _response(request, {"detail": "quantity debe ser un entero."}, 400)
    if quantity < 1:
        return _response(request, {"detail": "quantity debe ser mayor que cero."}, 400)

    try:
        variant = VarianteProducto.objects.get(varianteId=variant_id, activo=True)
    except VarianteProducto.DoesNotExist:
        return _response(request, {"detail": "La variante no existe o está inactiva."}, 404)

    item = Carrito.objects.filter(sesionId=session_id, varianteId=variant).first()
    if item:
        item.cantidad = quantity if request.method == "PATCH" else item.cantidad + quantity
        item.save(update_fields=["cantidad", "actualizadoEn"])
    else:
        item = Carrito.objects.create(
            idCarrito=f"CRT##{uuid4().hex[:6]}",
            sesionId=session_id,
            varianteId=variant,
            cantidad=quantity,
        )
    items = Carrito.objects.filter(sesionId=session_id).select_related("varianteId", "varianteId__idProducto")
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
    items = list(Carrito.objects.filter(sesionId=session_id).select_related("varianteId", "varianteId__idProducto"))
    if not items:
        return _response(request, {"detail": "El carrito está vacío."}, 400)

    shipping = Decimal("18000")
    subtotal = sum((item.varianteId.precio * item.cantidad for item in items), Decimal("0"))
    try:
        discount = Decimal(str(data.get("discount", "0")))
    except InvalidOperation:
        return _response(request, {"detail": "El descuento no es válido."}, 400)
    if discount < 0 or discount > 1:
        return _response(request, {"detail": "El descuento debe estar entre 0 y 1."}, 400)

    with transaction.atomic():
        order = Pedido.objects.create(
            idPedido=f"PD##{uuid4().hex[:6]}",
            numeroPedido=f"NMPD##{uuid4().hex[:6]}",
            estado=False,
            nombreCliente=str(data["name"]).strip(),
            apellidoCliente=str(data["lastName"]).strip(),
            emailContacto=str(data["email"]).strip(),
            telefonoContacto=str(data["phone"]).strip(),
            direccionDeEntrega=str(data["address"]).strip(),
            ciudadEntrega=str(data["city"]).strip(),
            descuento=discount,
            costoEnvio=shipping,
            total=(subtotal + shipping - (subtotal * discount)),
        )
        for item in items:
            line_total = item.varianteId.precio * item.cantidad
            DetallePedido.objects.create(
                idDetalle=f"DTP##{uuid4().hex[:6]}",
                idPedido=order,
                varianteId=item.varianteId,
                nombreProducto=item.varianteId.idProducto.nombre,
                sku=item.varianteId.sku,
                cantidad=item.cantidad,
                precioUnitario=item.varianteId.precio,
                subTotal=line_total,
            )
        Pago.objects.create(
            idPago=f"PG##{uuid4().hex[:6]}",
            pedidoId=order,
            metodo=str(data.get("paymentMethod", "Pendiente")),
            estado="Pendiente",
            monto=order.total,
            referencia=f"REF##{uuid4().hex[:6]}",
            fechaPago=timezone.now(),
            observaciones="Pago pendiente de confirmación.",
        )
        Carrito.objects.filter(sesionId=session_id).delete()

    return _response(request, {"orderId": order.idPedido, "orderNumber": order.numeroPedido, "total": _money(order.total)}, 201)
