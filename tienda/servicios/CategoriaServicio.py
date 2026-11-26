from django.core.exceptions import ValidationError
from django.db import transaction

from tienda.entidades import Categoria
from tienda.entidades.identificadores import generar_id


class CategoriaServicio:
    """Reglas de negocio para categorías."""

    @staticmethod
    def listaCategorias():
        return Categoria.objects.order_by("nombre")

    @staticmethod
    def buscarCategoria(categoriaId):
        return Categoria.objects.get(categoriaId=categoriaId)

    @staticmethod
    @transaction.atomic
    def crearCategoria(nombre, descripcion="", activa=True):
        nombre = str(nombre or "").strip()
        if not nombre:
            raise ValidationError("El nombre de categoría es obligatorio.")
        categoria = Categoria(
            categoriaId=f"CAT##{generar_id()}",
            nombre=nombre,
            descripcion=str(descripcion or "").strip(),
            activa=bool(activa),
        )
        categoria.full_clean()
        categoria.save()
        return categoria

    @staticmethod
    @transaction.atomic
    def actualizarCategoria(categoriaId, nombre, descripcion, activa=True):
        categoria = CategoriaServicio.buscarCategoria(categoriaId)
        categoria.nombre = str(nombre or "").strip()
        categoria.descripcion = str(descripcion or "").strip()
        categoria.activa = bool(activa)
        categoria.full_clean()
        categoria.save()
        return categoria

    @staticmethod
    @transaction.atomic
    def eliminarCategoria(categoriaId):
        categoria = CategoriaServicio.buscarCategoria(categoriaId)
        categoria.delete()
        return True
