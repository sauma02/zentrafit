from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from tienda.entidades import ImagenProducto, Producto, VarianteProducto
from tienda.entidades.identificadores import generar_id


class ProductoServicio:
    """Reglas de negocio para productos, variantes e imágenes."""

    @staticmethod
    def listaVariantes():
        return VarianteProducto.objects.select_related("idProducto").all()

    @staticmethod
    def mostrarCatalogo():
        return Producto.objects.filter(activo=True).select_related("categoriaId").prefetch_related("variantes", "imagenes")

    @staticmethod
    def mostrarTodosLosProductos():
        return Producto.objects.select_related("categoriaId").prefetch_related("variantes", "imagenes").all()

    @staticmethod
    def listarVarianteEspecifica(varianteId):
        return VarianteProducto.objects.select_related("idProducto").get(varianteId=varianteId)

    @staticmethod
    def encontrarProductoEspecifico(productoId):
        return Producto.objects.select_related("categoriaId").get(idProducto=productoId)

    @staticmethod
    def validarSku(sku, excluir_variante_id=None):
        query = VarianteProducto.objects.filter(sku=sku)
        if excluir_variante_id:
            query = query.exclude(varianteId=excluir_variante_id)
        if query.exists():
            raise ValidationError("El SKU debe ser único.")
        return True

    @staticmethod
    @transaction.atomic
    def registrarProductoNuevo(categoriaId, nombre, descripcion, marca, activo=True):
        ProductoServicio._validar_textos(nombre, marca)
        producto = Producto(
            idProducto=f"PROD##{generar_id()}",
            categoriaId=categoriaId,
            nombre=str(nombre).strip(),
            descripcion=str(descripcion or "").strip(),
            marca=str(marca).strip(),
            activo=bool(activo),
        )
        producto.full_clean()
        producto.save()
        return producto

    @staticmethod
    @transaction.atomic
    def nuevaVarianteDeProducto(productoId, sku, sabor, tamano, unidadMedida, precio, activo=True):
        producto = ProductoServicio.encontrarProductoEspecifico(productoId)
        ProductoServicio.validarSku(str(sku).strip())
        try:
            precio = Decimal(str(precio))
        except (InvalidOperation, TypeError):
            raise ValidationError("El precio no es válido.")
        if precio < 0:
            raise ValidationError("El precio no puede ser negativo.")
        variante = VarianteProducto(
            varianteId=f"VAR##{generar_id()}",
            idProducto=producto,
            sku=str(sku).strip(),
            sabor=str(sabor or "Sin sabor").strip(),
            tamano=str(tamano).strip(),
            unidadMedida=str(unidadMedida).strip(),
            precio=precio,
            activo=bool(activo),
        )
        variante.full_clean()
        variante.save()
        return variante

    @staticmethod
    @transaction.atomic
    def actualizarVariante(varianteId, productoId, sku, sabor, tamano, unidadMedida, precio, activo=True):
        variante = ProductoServicio.listarVarianteEspecifica(varianteId)
        producto = ProductoServicio.encontrarProductoEspecifico(productoId)
        ProductoServicio.validarSku(str(sku).strip(), excluir_variante_id=varianteId)
        try:
            precio = Decimal(str(precio))
        except (InvalidOperation, TypeError):
            raise ValidationError("El precio no es válido.")
        if precio < 0:
            raise ValidationError("El precio no puede ser negativo.")
        variante.idProducto = producto
        variante.sku = str(sku).strip()
        variante.sabor = str(sabor or "Sin sabor").strip()
        variante.tamano = str(tamano).strip()
        variante.unidadMedida = str(unidadMedida).strip()
        variante.precio = precio
        variante.activo = bool(activo)
        variante.full_clean()
        variante.save()
        return variante

    @staticmethod
    @transaction.atomic
    def actualizarProducto(productoId, categoriaId, nombre, descripcion, marca, activo=True):
        producto = ProductoServicio.encontrarProductoEspecifico(productoId)
        ProductoServicio._validar_textos(nombre, marca)
        producto.categoriaId = categoriaId
        producto.nombre = str(nombre).strip()
        producto.descripcion = str(descripcion or "").strip()
        producto.marca = str(marca).strip()
        producto.activo = bool(activo)
        producto.full_clean()
        producto.save()
        return producto

    @staticmethod
    @transaction.atomic
    def eliminarVariante(varianteId):
        variante = ProductoServicio.listarVarianteEspecifica(varianteId)
        variante.delete()
        return True

    @staticmethod
    @transaction.atomic
    def eliminarProducto(productoId):
        producto = ProductoServicio.encontrarProductoEspecifico(productoId)
        producto.delete()
        return True

    @staticmethod
    @transaction.atomic
    def asociarImagenes(productoId, archivoImagen, esPrincipal=False, ordenVisual=0):
        """Asocia un archivo subido a un producto mediante ImageField."""
        producto = ProductoServicio.encontrarProductoEspecifico(productoId)
        if not archivoImagen:
            raise ValidationError("El archivo de imagen es obligatorio.")
        if esPrincipal:
            ImagenProducto.objects.filter(idProducto=producto, esPrincipal=True).update(esPrincipal=False)
        imagen = ImagenProducto(
            idImagen=f"IMG##{generar_id()}",
            idProducto=producto,
            archivo=archivoImagen,
            esPrincipal=bool(esPrincipal),
            orden=ordenVisual,
        )
        imagen.full_clean()
        imagen.save()
        return imagen

    # Compatibilidad con el nombre original que ya existe en el proyecto.
    asosociarImagenes = asociarImagenes

    @staticmethod
    def _validar_textos(nombre, marca):
        if not str(nombre or "").strip() or not str(marca or "").strip():
            raise ValidationError("El nombre y la marca son obligatorios.")
