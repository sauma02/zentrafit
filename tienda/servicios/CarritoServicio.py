from entidades.Usuario import Usuario
from entidades.Carrito import Carrito
from datetime import Date
from entidades.VarianteProducto import VarianteProducto
from entidades.identificadores import generar_id
from servicios.ProductoServicio import ProductoServicio
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

from tienda.servicios import UsuarioServicio
class CarritoServicio():
    
    @staticmethod
    def listarCarrito(usuarioId, sesionId):
        try:
            if usuarioId:
                carrito=Carrito.objects.filter(usuarioId=usuarioId)
            elif sesionId:
                carrito=Carrito.objects.filter(sesionId=sesionId)
            else:
                raise ValidationError("Se requiere un ID de usuario o un ID de sesión para listar el carrito")
            if not carrito.exists():
                raise ValidationError("El carrito esta vacio")
            return carrito
        except ObjectDoesNotExist as e:
            print(f"Error, el objeto no existe: {e}")
        except IntegrityError as e:
            print(f"Error fatal(Listar carrito): {e}")
    @staticmethod
    def agregarItem(usuarioId, varianteId, cantidad, sesionId=None):
        
        try:
            if cantidad <=0:
                raise ValueError("La cantidad no puede ser 0")
            varianteProducto=ProductoServicio.listarVarianteEspecifica(varianteId)
            if not varianteProducto.exists():
                raise ValidationError("La variante de producto no existe")
            usuario = None
            if usuarioId is not None:
                try:
                    usuario = UsuarioServicio.listarUsuarioEspecifico(usuarioId)
                except ObjectDoesNotExist:
                    raise ValidationError("El usuario no existe")
            if usuario:
                itemExistente=Carrito.objects.filter(usuario=usuario, varianteProducto=varianteProducto).first( )
            else:
                if not sesionId:
                    raise ValidationError("Se requiere un ID de sesión para usuarios no autenticados")
                itemExistente=Carrito.objects.filter(usuarioId_isnull=True, sesionId=sesionId, varianteProducto=varianteProducto).first( )
            if itemExistente:
                itemExistente.cantidad += cantidad
                itemExistente.actualizadoEn=Date.today()
                itemExistente.save()
                return itemExistente
            else:
                idCombinado=f"CRT##{generar_id()}"
                idCarrito=idCombinado
                idSesionFinal = sesionId if sesionId else f"SES##{generar_id()}"
                carrito=Carrito(
                    id=idCarrito,
                    usuario=usuario,
                    sesionId=idSesionFinal,
                    varianteProducto=varianteProducto,
                    cantidad=cantidad,
                    creadoEn=Date.today(),
                    actualizadoEn=Date.today()
                )
                carrito.save()
                return carrito


            
            
        except ObjectDoesNotExist as e:
            print(f"Error, el objeto no existe: {e}")
        except IntegrityError as e:
            print(f"Error fatal(Agregar item al carrito): {e}")
            
            




