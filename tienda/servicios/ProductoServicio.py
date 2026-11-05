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

from tienda.entidades.ImagenProducto import ImagenProducto


class ProductoServicio():

    
    @staticmethod
    def listaVariantes():
         try:
              listaVariantes = VarianteProducto.objects.all()
              if not listaVariantes.exists():
                   raise ValidationError("La lista esta vacia, no hay variantes pegadas")
              return listaVariantes
         except IntegrityError as e:
              print(f"Error fatal(ListarVariantes): {e}")
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
    def validarSku(sku):
        try:
              listaVariantes=ProductoServicio.listaVariantes()
              for variantes in listaVariantes:
                   if sku == variantes.sku:
                        raise IntegrityError("Error fatal(Validar sku): El sku debe ser unico")
                   else:
                        return "El sku es unico, no se encuentra registrado"
        except IntegrityError as e:
             print(f"Error fatal(Validar sku): {e}")
    @staticmethod
    def listarVarianteEspecifica(varianteId):
         try:
              varianteAEncontrar = VarianteProducto.objects.filter(varianteId=varianteId)
              return varianteAEncontrar
         except ObjectDoesNotExist as e:
              print(f"Error, variante no encontrada o no existe: {e}")

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
    def nuevaVarianteDeProducto(productoId, sku, sabor, tamano, unidadMedida, precio):
        try:
             idCombinado = f"VRP##{generar_id}"
             if precio <= 0:
                print("El precio tiene que ser mayor a 0") 
             ProductoServicio.validarSku(sku)
             producto=ProductoServicio.encontrarProductoEspecifico(productoId)
             if producto == None:
                  raise ObjectDoesNotExist("Error, el objeto no existe")
             variante=VarianteProducto(varianteId=idCombinado, idProducto=producto, sku=sku, sabor=sabor, tamano=tamano,
                                       unidadMedida=unidadMedida, precio=precio)
             variante.full_clean()
             variante.save()
        except ValidationError as e:
             print(f"Error critico, uno o mas espacios estan vacios")
        except IntegrityError as e:
             print(f"Error fatal(Registrar Variante): {e}") 
    @staticmethod
    def eliminarVariante(varianteId):
        try:
              varianteEliminar=ProductoServicio.listarVarianteEspecifica(varianteId)
              if varianteEliminar == None:
                   raise ValidationError
              varianteEliminar.delete()
              print("Variante eliminada con exito")
        except IntegrityError as e:
             print(f"Error fatal(Eliminar variante): {e}")
              
    @staticmethod
    def actualizarVariante(varianteId, productoId, sku, sabor, tamano, unidadMedida, precio, activo):
        try:

              if precio <= 0:
                   raise ValueError("El precio tiene que ser mayor a 0")  
              varianteActualizado=ProductoServicio.listarVarianteEspecifica(varianteId)
              productoActualizado=ProductoServicio.encontrarProductoEspecifico(productoId)
              ProductoServicio.validarSku(sku)
              varianteActualizado.productoId=productoActualizado
              varianteActualizado.sku=sku
              varianteActualizado.sabor=sabor
              varianteActualizado.tamano=tamano
              varianteActualizado.unidadMedida = unidadMedida
              varianteActualizado.precio=precio
              varianteActualizado.activo=activo
              varianteActualizado.save()
        except ObjectDoesNotExist as e:
             print(f"Error,la variante o el producto no pudo ser encontrado o no existe: {e}")
        except IntegrityError as e:
             print(f"Error fatal(Actualizar variante): {e}")
    
            
    @staticmethod
    def actualizarProducto(productoId,categoriaId, nombre, descripcion, marca, activo):
        try:
           productoActualizado=ProductoServicio.encontrarProductoEspecifico(productoId)
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
    @staticmethod
    def asosociarImagenes(productoId, rutaImagen, esPrincipal=False, ordenVisual=1):
        try:
             producto=ProductoServicio.encontrarProductoEspecifico(productoId)
             if producto == None or not producto.exists():
                raise ObjectDoesNotExist("Error, el objeto no existe")
             idCombinado=f"IMG##{generar_id()}"
             imagenId=idCombinado
             imagen=ImagenProducto(idImagen=imagenId, idProducto=producto, archivo=rutaImagen, esPrincipal=esPrincipal, orden=ordenVisual)
             imagen.full_clean()
             imagen.save()
        except ValidationError as e:
             print(f"Error critico, uno o mas espacios estan vacios")
        except IntegrityError as e:
             print(f"Error fatal(Asociar imagen): {e}")
        except ObjectDoesNotExist as e:
             print(f"Error, producto no encontrado o no existe: {e}")
    
