import json
import re

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from tienda.entidades import Categoria
from tienda.servicios.AdministracionServicio import AdministracionServicio
from tienda.servicios.CategoriaServicio import CategoriaServicio
from tienda.servicios.InventarioServicio import InventarioServicio
from tienda.servicios.ProductoServicio import ProductoServicio


def _with_cors(request, response):
    origin = request.headers.get("Origin", "")
    if (
        origin.endswith(".app.github.dev")
        or origin.endswith(".manus.computer")
        or re.match(r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$", origin)
    ):
        response["Access-Control-Allow-Origin"] = origin
        response["Access-Control-Allow-Credentials"] = "true"
        response["Access-Control-Allow-Methods"] = "GET, POST, PATCH, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Accept, Content-Type, X-CSRFToken"
        response["Vary"] = "Origin"
    return response


def _admin_only(view):
    def wrapped(request, *args, **kwargs):
        # El dashboard depende de una sesión staff de Django. Un 403 aquí no
        # es un error de React: significa que hay que iniciar sesión en /admin/.
        if request.method == "OPTIONS":
            return _with_cors(request, JsonResponse({}))
        if not request.user.is_authenticated or not request.user.is_staff:
            return _with_cors(request, JsonResponse({"detail": "Debes iniciar sesión como administrador."}, status=403))
        return _with_cors(request, view(request, *args, **kwargs))

    return wrapped


def _body(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


def _stock(variant):
    return InventarioServicio.calcularStock(variant)


def _variant(variant):
    return {
        "id": variant.varianteId,
        "sku": variant.sku,
        "flavor": variant.sabor,
        "size": variant.tamano,
        "unit": variant.unidadMedida,
        "price": float(variant.precio),
        "active": variant.activo,
        "stock": _stock(variant),
    }


def _product(product):
    return {
        "id": product.idProducto,
        "name": product.nombre,
        "description": product.descripcion,
        "brand": product.marca,
        "active": product.activo,
        "categoryId": product.categoriaId_id,
        "category": product.categoriaId.nombre,
        "variants": [_variant(item) for item in product.variantes.all()],
    }


def _category(category):
    return {
        "id": category.categoriaId,
        "name": category.nombre,
        "description": category.descripcion,
        "active": category.activa,
    }


def _image(image, request=None):
    url = image.archivo.url if image.archivo else None
    return {
        "id": image.idImagen,
        "productId": image.idProducto_id,
        "url": request.build_absolute_uri(url) if request and url else url,
        "isPrimary": image.esPrincipal,
        "order": image.orden,
    }


def _order(order):
    return {
        "id": order.idPedido,
        "number": order.numeroPedido,
        "customer": f"{order.nombreCliente} {order.apellidoCliente}",
        "email": order.emailContacto,
        "city": order.ciudadEntrega,
        "total": float(order.total),
        "status": "Completado" if order.estado else "Pendiente",
        "date": order.fechaPedido.isoformat(),
        "items": [
            {"name": detail.nombreProducto, "sku": detail.sku, "quantity": detail.cantidad, "subtotal": float(detail.subTotal)}
            for detail in order.detalles.all()
        ],
    }


@_admin_only
@require_http_methods(["GET", "OPTIONS"])
def overview(request):
    if request.method == "OPTIONS":
        return JsonResponse({})
    summary = AdministracionServicio.resumen()
    return JsonResponse({
        "metrics": {
            "products": len(summary["products"]),
            "variants": len(summary["variants"]),
            "categories": summary["categories"],
            "pendingOrders": summary["pending_orders"],
            "revenue": float(summary["revenue"]),
        },
        "lowStock": summary["low_stock"],
        "orders": [_order(order) for order in summary["orders"]],
    })


@_admin_only
@require_http_methods(["GET", "POST", "OPTIONS"])
@csrf_protect
def categories(request):
    if request.method == "OPTIONS":
        return JsonResponse({})
    if request.method == "GET":
        return JsonResponse({"categories": [_category(item) for item in CategoriaServicio.listaCategorias()]})
    data = _body(request)
    if not data:
        return JsonResponse({"detail": "JSON inválido."}, status=400)
    try:
        category = CategoriaServicio.crearCategoria(data.get("name"), data.get("description", ""), data.get("active", True))
    except ValidationError as error:
        return JsonResponse({"detail": error.messages[0]}, status=400)
    return JsonResponse(_category(category), status=201)


@_admin_only
@require_http_methods(["GET", "POST", "OPTIONS"])
@csrf_protect
def products(request):
    if request.method == "OPTIONS":
        return JsonResponse({})
    if request.method == "GET":
        return JsonResponse({"products": [_product(item) for item in ProductoServicio.mostrarTodosLosProductos()]})
    data = _body(request)
    if not data:
        return JsonResponse({"detail": "JSON inválido."}, status=400)
    try:
        category = CategoriaServicio.buscarCategoria(data.get("categoryId"))
        product = ProductoServicio.registrarProductoNuevo(
            categoriaId=category,
            nombre=data.get("name"),
            descripcion=data.get("description", ""),
            marca=data.get("brand"),
            activo=data.get("active", True),
        )
    except Categoria.DoesNotExist:
        return JsonResponse({"detail": "Categoría no encontrada."}, status=404)
    except ValidationError as error:
        return JsonResponse({"detail": error.messages[0]}, status=400)
    except ObjectDoesNotExist:
        return JsonResponse({"detail": "Categoría no encontrada."}, status=404)
    return JsonResponse(_product(product), status=201)


@_admin_only
@require_http_methods(["POST", "OPTIONS"])
@csrf_protect
def variants(request):
    if request.method == "OPTIONS":
        return JsonResponse({})
    data = _body(request)
    if not data:
        return JsonResponse({"detail": "JSON inválido."}, status=400)
    try:
        variant = ProductoServicio.nuevaVarianteDeProducto(
            productoId=data.get("productId"),
            sku=data.get("sku"),
            sabor=data.get("flavor", "Sin sabor"),
            tamano=data.get("size"),
            unidadMedida=data.get("unit"),
            precio=data.get("price"),
            activo=data.get("active", True),
        )
    except ObjectDoesNotExist:
        return JsonResponse({"detail": "Producto no encontrado."}, status=404)
    except ValidationError as error:
        return JsonResponse({"detail": error.messages[0]}, status=400)
    return JsonResponse(_variant(variant), status=201)


@_admin_only
@require_http_methods(["POST", "OPTIONS"])
@csrf_protect
def images(request):
    if request.method == "OPTIONS":
        return JsonResponse({})
    product_id = request.POST.get("productId")
    archivo = request.FILES.get("archivo")
    # FormData llega en request.FILES; la vista valida transporte y permisos,
    # mientras ProductoServicio conserva las reglas de negocio MVC.
    if not product_id or not archivo:
        return JsonResponse({"detail": "Producto y archivo son obligatorios."}, status=400)
    try:
        orden = int(request.POST.get("order", 0))
        is_primary = request.POST.get("isPrimary", "false").lower() in {"true", "1", "on", "yes"}
        image = ProductoServicio.asociarImagenes(product_id, archivo, is_primary, orden)
    except ObjectDoesNotExist:
        return JsonResponse({"detail": "Producto no encontrado."}, status=404)
    except (ValidationError, ValueError) as error:
        detail = error.messages[0] if isinstance(error, ValidationError) else "El orden no es válido."
        return JsonResponse({"detail": detail}, status=400)
    return JsonResponse(_image(image, request), status=201)


@_admin_only
@require_http_methods(["GET", "POST", "OPTIONS"])
@csrf_protect
def inventory(request):
    if request.method == "OPTIONS":
        return JsonResponse({})
    if request.method == "GET":
        variants = InventarioServicio.listarVariantesConStock()
        return JsonResponse({"inventory": [{"variantId": item.varianteId, "product": item.idProducto.nombre, "sku": item.sku, "stock": _stock(item), "price": float(item.precio)} for item in variants]})
    data = _body(request)
    if not data:
        return JsonResponse({"detail": "JSON inválido."}, status=400)
    try:
        movement = InventarioServicio.registrarMovimiento(
            varianteId=data.get("variantId"),
            tipo=data.get("type"),
            cantidad=data.get("quantity", 0),
            motivo=data.get("reason", "Ajuste administrativo"),
            observaciones=data.get("notes", ""),
        )
    except ObjectDoesNotExist:
        return JsonResponse({"detail": "Variante no encontrada."}, status=404)
    except ValidationError as error:
        return JsonResponse({"detail": error.messages[0]}, status=400)
    return JsonResponse({"id": movement.idMovimientoInventario, "stock": _stock(movement.varianteId)}, status=201)


@_admin_only
@require_http_methods(["GET", "PATCH", "OPTIONS"])
@csrf_protect
def orders(request):
    if request.method == "OPTIONS":
        return JsonResponse({})
    if request.method == "GET":
        return JsonResponse({"orders": [_order(order) for order in AdministracionServicio.listarPedidos()]})
    data = _body(request)
    if not data or not data.get("id"):
        return JsonResponse({"detail": "id es obligatorio."}, status=400)
    try:
        order = AdministracionServicio.actualizarEstadoPedido(data["id"], str(data.get("status", "")).lower() in {"completado", "true", "1"})
    except ObjectDoesNotExist:
        return JsonResponse({"detail": "Pedido no encontrado."}, status=404)
    return JsonResponse(_order(order))
