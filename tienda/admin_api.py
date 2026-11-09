import json
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from tienda.entidades import Categoria, DetallePedido, MovimientoInventario, Pedido, Producto, VarianteProducto


def _admin_only(view):
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return JsonResponse({"detail": "Debes iniciar sesión como administrador."}, status=403)
        return view(request, *args, **kwargs)
    return wrapped


def _body(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


def _id(prefix):
    return f"{prefix}##{uuid4().hex[:8]}"


def _stock(variant):
    movements = MovimientoInventario.objects.filter(varianteId=variant)
    return sum((movement.cantidad if movement.tipo == "entrada" else -movement.cantidad for movement in movements), 0)


def _variant(variant):
    return {"id": variant.varianteId, "sku": variant.sku, "flavor": variant.sabor, "size": variant.tamano, "unit": variant.unidadMedida, "price": float(variant.precio), "active": variant.activo, "stock": _stock(variant)}


def _product(product):
    return {"id": product.idProducto, "name": product.nombre, "description": product.descripcion, "brand": product.marca, "active": product.activo, "categoryId": product.categoriaId_id, "category": product.categoriaId.nombre, "variants": [_variant(item) for item in product.variantes.all()]}


def _order(order):
    return {"id": order.idPedido, "number": order.numeroPedido, "customer": f"{order.nombreCliente} {order.apellidoCliente}", "email": order.emailContacto, "city": order.ciudadEntrega, "total": float(order.total), "status": "Completado" if order.estado else "Pendiente", "date": order.fechaPedido.isoformat(), "items": [{"name": detail.nombreProducto, "sku": detail.sku, "quantity": detail.cantidad, "subtotal": float(detail.subTotal)} for detail in order.detalles.all()]}


@_admin_only
@require_http_methods(["GET", "OPTIONS"])
def overview(request):
    if request.method == "OPTIONS":
        return JsonResponse({})
    products = list(Producto.objects.select_related("categoriaId").prefetch_related("variantes"))
    variants = [variant for product in products for variant in product.variantes.all()]
    orders = list(Pedido.objects.prefetch_related("detalles").order_by("-fechaPedido")[:8])
    return JsonResponse({"metrics": {"products": len(products), "variants": len(variants), "categories": Categoria.objects.filter(activa=True).count(), "pendingOrders": Pedido.objects.filter(estado=False).count(), "revenue": float(sum((order.total for order in Pedido.objects.filter(estado=True)), Decimal("0")))}, "lowStock": [{"product": variant.idProducto.nombre, "sku": variant.sku, "stock": _stock(variant)} for variant in variants if _stock(variant) <= 5], "orders": [_order(order) for order in orders]})


@_admin_only
@require_http_methods(["GET", "POST", "OPTIONS"])
@csrf_protect
def categories(request):
    if request.method == "OPTIONS":
        return JsonResponse({})
    if request.method == "GET":
        return JsonResponse({"categories": [{"id": item.categoriaId, "name": item.nombre, "description": item.descripcion, "active": item.activa} for item in Categoria.objects.order_by("nombre")]})
    data = _body(request)
    if not data or not str(data.get("name", "")).strip():
        return JsonResponse({"detail": "El nombre de categoría es obligatorio."}, status=400)
    category = Categoria.objects.create(categoriaId=_id("CAT"), nombre=str(data["name"]).strip(), descripcion=str(data.get("description", "")).strip(), activa=bool(data.get("active", True)))
    return JsonResponse({"id": category.categoriaId, "name": category.nombre}, status=201)


@_admin_only
@require_http_methods(["GET", "POST", "OPTIONS"])
@csrf_protect
def products(request):
    if request.method == "OPTIONS":
        return JsonResponse({})
    if request.method == "GET":
        return JsonResponse({"products": [_product(item) for item in Producto.objects.select_related("categoriaId").prefetch_related("variantes").order_by("-fechaCreacion")]})
    data = _body(request)
    required = ["name", "categoryId", "brand"]
    if not data or any(not str(data.get(field, "")).strip() for field in required):
        return JsonResponse({"detail": "name, categoryId y brand son obligatorios."}, status=400)
    try:
        category = Categoria.objects.get(categoriaId=data["categoryId"])
    except Categoria.DoesNotExist:
        return JsonResponse({"detail": "Categoría no encontrada."}, status=404)
    product = Producto.objects.create(idProducto=_id("PROD"), categoriaId=category, nombre=str(data["name"]).strip(), descripcion=str(data.get("description", "")).strip(), marca=str(data["brand"]).strip(), activo=bool(data.get("active", True)))
    return JsonResponse(_product(product), status=201)


@_admin_only
@require_http_methods(["POST", "OPTIONS"])
@csrf_protect
def variants(request):
    if request.method == "OPTIONS":
        return JsonResponse({})
    data = _body(request)
    required = ["productId", "sku", "size", "unit", "price"]
    if not data or any(not str(data.get(field, "")).strip() for field in required):
        return JsonResponse({"detail": "productId, sku, size, unit y price son obligatorios."}, status=400)
    try:
        product = Producto.objects.get(idProducto=data["productId"])
        price = Decimal(str(data["price"]))
    except (Producto.DoesNotExist, InvalidOperation):
        return JsonResponse({"detail": "Producto o precio inválido."}, status=400)
    if price < 0:
        return JsonResponse({"detail": "El precio no puede ser negativo."}, status=400)
    variant = VarianteProducto.objects.create(varianteId=_id("VAR"), idProducto=product, sku=str(data["sku"]).strip(), sabor=str(data.get("flavor", "Sin sabor")).strip(), tamano=str(data["size"]).strip(), unidadMedida=str(data["unit"]).strip(), precio=price, activo=bool(data.get("active", True)))
    return JsonResponse(_variant(variant), status=201)


@_admin_only
@require_http_methods(["GET", "POST", "OPTIONS"])
@csrf_protect
def inventory(request):
    if request.method == "OPTIONS":
        return JsonResponse({})
    if request.method == "GET":
        variants = VarianteProducto.objects.select_related("idProducto").order_by("sku")
        return JsonResponse({"inventory": [{"variantId": item.varianteId, "product": item.idProducto.nombre, "sku": item.sku, "stock": _stock(item), "price": float(item.precio)} for item in variants]})
    data = _body(request)
    if not data or not data.get("variantId") or data.get("type") not in {"entrada", "salida", "ajuste"}:
        return JsonResponse({"detail": "variantId y type válido son obligatorios."}, status=400)
    try:
        quantity = int(data.get("quantity", 0))
        variant = VarianteProducto.objects.get(varianteId=data["variantId"])
    except (ValueError, VarianteProducto.DoesNotExist):
        return JsonResponse({"detail": "Variante o cantidad inválida."}, status=400)
    if quantity <= 0:
        return JsonResponse({"detail": "La cantidad debe ser mayor que cero."}, status=400)
    movement = MovimientoInventario.objects.create(idMovimientoInventario=_id("MOV"), varianteId=variant, tipo=data["type"], cantidad=quantity, motivo=str(data.get("reason", "Ajuste administrativo"))[:100], observaciones=str(data.get("notes", "")))
    return JsonResponse({"id": movement.idMovimientoInventario, "stock": _stock(variant)}, status=201)


@_admin_only
@require_http_methods(["GET", "PATCH", "OPTIONS"])
@csrf_protect
def orders(request):
    if request.method == "OPTIONS":
        return JsonResponse({})
    if request.method == "GET":
        return JsonResponse({"orders": [_order(order) for order in Pedido.objects.prefetch_related("detalles").order_by("-fechaPedido")]})
    data = _body(request)
    order_id = data.get("id") if data else None
    if not order_id:
        return JsonResponse({"detail": "id es obligatorio."}, status=400)
    try:
        order = Pedido.objects.get(idPedido=order_id)
    except Pedido.DoesNotExist:
        return JsonResponse({"detail": "Pedido no encontrado."}, status=404)
    order.estado = str(data.get("status", "")).lower() in {"completado", "true", "1"}
    order.save(update_fields=["estado"])
    return JsonResponse(_order(order))
