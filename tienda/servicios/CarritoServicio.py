from tienda.entidades.Usuario import Usuario
from tienda.entidades.Carrito import Carrito
from datetime import date as Date
from tienda.entidades.VarianteProducto import VarianteProducto
from tienda.entidades.identificadores import generar_id
from tienda.servicios.ProductoServicio import ProductoServicio
from django.db import IntegrityError, DataError, OperationalError, transaction
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
    def listarCarrito(sesionId):
        try:
            if sesionId:
                carrito=Carrito.objects.filter(sesionId=sesionId)
            else:
                raise ValidationError("Se requiere un ID de usuario o un ID de sesión para listar el carrito")
            return carrito
        except ObjectDoesNotExist as e:
            print(f"Error, el objeto no existe: {e}")
        except IntegrityError as e:
            print(f"Error fatal(Listar carrito): {e}")
    @transaction.atomic
    @staticmethod
    def agregarItem(usuarioId, varianteId, cantidad, sesionId):
        
        try:
            if cantidad <=0:
                raise ValueError("La cantidad no puede ser 0")
            varianteProducto=ProductoServicio.listarVarianteEspecifica(varianteId)
            if not varianteProducto:
                raise ValidationError("La variante de producto no existe")
            usuario = None
            if usuarioId is not None:
                try:
                    usuario = UsuarioServicio.listarUsuarioEspecifico(usuarioId)
                except ObjectDoesNotExist:
                    raise ValidationError("El usuario no existe")
            if usuario:
                itemExistente=Carrito.objects.get(usuario=usuario, varianteId=varianteProducto)
            else:
                if not sesionId:
                    raise ValidationError("Se requiere un ID de sesión para usuarios no autenticados")
                itemExistente=Carrito.objects.get(usuarioId=usuarioId, sesionId=sesionId, varianteId=varianteProducto)
            if itemExistente:
                itemExistente.cantidad += cantidad
                itemExistente.actualizadoEn=Date.today()
                itemExistente.save()
                return itemExistente
            else:
                idCombinado = f"CRT##{generar_id()}"
                idSesionFinal = sesionId if sesionId is not None else f"SES##{generar_id()}"
                
                # 🚀 USAMOS objects.create PARA INPACTAR LA BD DIRECTAMENTE EN UNA SOLA LÍNEA SQL
                carrito_guardado = Carrito.objects.create(
                    idCarrito=idCombinado,           # Revisa que en tu archivo de entidades se llame exactamente 'idCarrito'
                    usuarioId=usuario,               # Debe apuntar al objeto Usuario o ser None
                    sesionId=idSesionFinal,
                    varianteId=varianteProducto,     # Debe apuntar al objeto VarianteProducto extraído
                    cantidad=cantidad,
                    fechaCreacion=Date.today(),
                    actualizadoEn=Date.today()
                )
                
                print(f" Confirmación: ¡Carrito insertado en la Base de Datos con ID {idCombinado}!")
                return carrito_guardado


            
            
        except ObjectDoesNotExist as e:
            print(f"Error, el objeto no existe: {e}")
        except IntegrityError as e:
            print(f"Error fatal(Agregar item al carrito): {e}")
            
            




