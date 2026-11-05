from datetime import date as Date
from django.db import transaction
from django.core.exceptions import ValidationError

from tienda.entidades.Usuario import Usuario
from tienda.entidades.Carrito import Carrito
from tienda.entidades.VarianteProducto import VarianteProducto
from tienda.entidades.identificadores import generar_id
from tienda.servicios.ProductoServicio import ProductoServicio
from tienda.servicios import UsuarioServicio

class CarritoServicio():
    
    @transaction.atomic
    @staticmethod
    def listarCarrito(sesionId):
        try:
            
            if sesionId:
                carrito = Carrito.objects.filter(sesionId=sesionId)
            else:
                raise ValidationError("Se requiere un ID de usuario o un ID de sesión para listar el carrito")
            
            if not carrito.exists():
                raise ValidationError("El carrito esta vacio")
            return carrito
        except Exception as e:
            print(f"Error al listar carrito: {e}")
            return None

    @transaction.atomic
    @staticmethod
    def agregarItem(usuarioId, varianteId, cantidad, sesionId=None):
        try:
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor a 0")
            
            # 1. Recuperar la instancia de la variante
            variante_queryset = ProductoServicio.listarVarianteEspecifica(varianteId)
            if hasattr(variante_queryset, 'exists') and not variante_queryset.exists():
                raise ValidationError("La variante de producto no existe")
                
            varianteProducto = variante_queryset.first() if hasattr(variante_queryset, 'first') else variante_queryset
            
            # 2. Gestionar usuario (Soporta Invitados si viene None)
            usuario = None
            if usuarioId is not None and usuarioId != "":
                try:
                    user_res = UsuarioServicio.listarUsuarioEspecifico(usuarioId)
                    usuario = user_res.first() if hasattr(user_res, 'first') else user_res
                except Exception:
                    raise ValidationError("El usuario no existe")
            
            # 3. Buscar ítem existente alineado a las propiedades físicas de Carrito.py
            if usuario:
                itemExistente = Carrito.objects.filter(usuarioId=usuario, varianteId=varianteProducto).first()
            else:
                if not sesionId:
                    raise ValidationError("Se requiere un ID de sesión para usuarios no autenticados")
                itemExistente = Carrito.objects.filter(usuarioId=usuario, sesionId=sesionId, varianteId=varianteProducto).first()
            
            # 4. Actualizar cantidad o Insertar nuevo registro físico en SQL
            if itemExistente:
                itemExistente.cantidad += cantidad
                itemExistente.actualizadoEn = Date.today()
                itemExistente.save()
                print(f"📦 Cantidad actualizada en BD para el carrito {itemExistente.idCarrito}")
                return itemExistente
            else:
                # Forzamos IDs combinados seguros
                idCombinado = f"CRT##{generar_id()}"
                idSesionFinal = sesionId if sesionId is not None else f"SES##{generar_id()}"
                
                # 🚀 USAMOS objects.create DIRECTO PARA PERSISTIR EN SQL INMEDIATAMENTE
                nuevo_carrito = Carrito.objects.create(
                    idCarrito=idCombinado,            # Nombre del atributo en tu Carrito.py
                    usuarioId=usuario,                  # Instancia de Usuario o None
                    sesionId=idSesionFinal,
                    varianteId=varianteProducto,# Instancia de VarianteProducto
                    cantidad=cantidad,
                    fechaCreacion=Date.today(),            # Nombre del atributo en tu Carrito.py
                    actualizadoEn=Date.today()
                )
                print(f"💾 ¡Registro insertado exitosamente en la Base de Datos con ID: {idCombinado}!")
                return nuevo_carrito
                
        except Exception as e:
            print(f"❌ Error crítico en agregarItem: {e}")
            raise e