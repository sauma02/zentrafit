from entidades.Categoria import Categoria
from entidades.identificadores import generar_id
from django.db import IntegrityError, DataError, OperationalError
from django.core.exceptions import (
    NON_FIELD_ERRORS,
    FieldDoesNotExist,
    FieldError,
    MultipleObjectsReturned,
    ObjectDoesNotExist,
    ObjectNotUpdated,
    ValidationError,
)

class CategoriaServicio():
    @staticmethod
    def listaCategorias():
        try:
            listaCategorias = Categoria.objects.all()
            if not listaCategorias.exists():
                raise ValidationError("La lista esta vacia")
            return listaCategorias
        except IntegrityError as e:
            print(f"Error fatal(Funcion listaCategorias): {e}")

    @staticmethod
    def crearCategoria(nombre, descripcion):
        try:
            idCombinado = f"CT##{generar_id}"
            categoriaNueva=Categoria(categoriaId=idCombinado, nombre=nombre, descripcion=descripcion)
            categoriaNueva.full_clean()
            categoriaNueva.save()
            return categoriaNueva
        except ValidationError as e:
            print(f"Error critico, uno o mas campos estan vacios: {e}")
        except IntegrityError as e:
                    print(f"Error Fatal(Registrar Categoria): {e}")    

    @staticmethod
    def actualizarCategoria(categoriaId, nombre, descripcion, activo):
        try:
            categoriaActualizada=Categoria.objects.filter(categoriaId=categoriaId)
            categoriaActualizada.nombre = nombre
            categoriaActualizada.descripcion= descripcion
            categoriaActualizada.activo=activo
            categoriaActualizada.save()
            return categoriaActualizada
        except ObjectDoesNotExist as e:
            print(f"El producto no existe o no pudo ser encontrad para actualizar: {e}")
        except IntegrityError as e:
                    print(f"Error Fatal(Actualizar Categoria): {e}")
    @staticmethod
    def eliminarCategoria(categoriaId):
        try:
            categoriaEliminada=Categoria.objects.filter(categoriaId=categoriaId)
            categoriaEliminada.delete()
            print("Producto eliminado con exito")
        except ObjectDoesNotExist as e:
            print(f"El producto a elimnar no existe: {e}")
        except IntegrityError as e:
            print(f"Error Fatal(Eliminar Categoria): {e}")

    