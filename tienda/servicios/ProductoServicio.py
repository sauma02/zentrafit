from entidades.Producto import Producto
from entidades.VarianteProducto import VarianteProducto
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


class ProductoServicio():

    

    @staticmethod
    def mostrarCatalogo():
        try:
        ##Se traen solo los productos registrados activos
            listaCatalogo = Producto.objects.filter(activo=True)
            if not listaCatalogo.exists():
                raise ValidationError("La lista esta vacia, no hay catalogo")
            return listaCatalogo
        except IntegrityError as e:
            print(f"Error fatal(Funcion mostrarCatologo): {e}")
    @staticmethod
    def mostrarTodosLosProductos():
        try:
            ##Funcion para listas todos lo productos registrados, activos e inactivos
            listaProductos = Producto.objects.all()
            if not listaProductos.exists():
                raise ValidationError("No hay productos registrados")
            return listaProductos
        except IntegrityError as e:
            print(f"Error Fatal(Funcion mostrar productos): {e}")
            
            
    @staticmethod
    def registrarProductoNuevo(categoriaId, nombre, descripcion, marca):
        try:
            idCombinado=f"PD#{generar_id}"
            productoNuevo = Producto(idProducto=idCombinado, categoriaId=categoriaId, nombre=nombre, descripcion=descripcion, marca=marca)
            productoNuevo.full_clean()
            productoNuevo.save()
            return productoNuevo
        except ValidationError as e:
            print(f"Error critico, uno o mas campos estan vacios: {e}")
        except IntegrityError as e:
                    print(f"Error fatal(Registrar Producto): {e}")
           
            
    @staticmethod
    def actualizarProducto(productoId,categoriaId, nombre, descripcion, marca, activo):
        try:
           productoActualizado=Producto.objects.filter(idProducto=productoId)
           productoActualizado.categoriaId=categoriaId
           productoActualizado.nombre=nombre
           productoActualizado.descripcion=descripcion
           productoActualizado.marca=marca
           productoActualizado.activo=activo
           productoActualizado.save()
           return productoActualizado
        except ObjectDoesNotExist as e:
            print(f"Error, no existe este producto, no se puede editar: {e}")
        except IntegrityError as e:
                    print(f"Error fatal(Actualizar producto): {e}")
    @staticmethod
    def eliminarProducto(productoId):
        try:
            productoEliminado=Producto.objects.filter(idProducto=productoId)
            productoEliminado.delete()
            return "Producto eliminado con exito"
        except ObjectDoesNotExist as e:
            print(f"El producto a eliminar no existe: {e}")
        except IntegrityError as e:
            print(f"Error fatal(Eliminar producto): {e}")
    @staticmethod
    def encontrarProductoEspecifico(productoId):
        try:
            productoEncontrado=Producto.objects.filter(idProduto=productoId)
            return productoEncontrado
        except ObjectDoesNotExist as e:
            print(f"Error, producto no encontrado o no existe: {e}")
        
        
    
