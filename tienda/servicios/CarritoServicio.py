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
class CarritoServicio():

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
                usuario = Usuario.objects.filter(id=usuarioId).first()

            
            
        except ObjectDoesNotExist as e:
            print(f"Error, el objeto no existe: {e}")
        except IntegrityError as e:
            print(f"Error fatal(Agregar item al carrito): {e}")
            
            




