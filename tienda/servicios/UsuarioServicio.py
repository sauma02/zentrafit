from entidades.Usuario import Usuario
from django.db import IntegrityError, DataError, OperationalError
from entidades.identificadores import generar_id
from django.core.exceptions import (
    NON_FIELD_ERRORS,
    FieldDoesNotExist,
    FieldError,
    MultipleObjectsReturned,
    ObjectDoesNotExist,
    ObjectNotUpdated,
    ValidationError,
)
class ServicioUsuario():

    @staticmethod
    def listarUsuarios():
        try:
            listaUsuarios = Usuario.objects.all()
            if not listaUsuarios.exists():
                raise ValidationError("No hay usuarios registrados")
            return listaUsuarios
        except IntegrityError as e:
            print(f"Error Fatal(Listar usuarios): {e}")
    @staticmethod
    def buscarUsuario(usuarioId):
        try:
            usuario=Usuario.objects.filter(id=usuarioId)
            if not usuario.exists():
                raise ValidationError("El usuario que trata de buscar no existe")
            return usuario
        except IntegrityError as e:
            print(f"Error Fatal(Buscar usuario): {e}")
    @staticmethod
    def crearUsuarioStaff(nombre, apellido, password, edad, correo, esAdmin, esStaff, contacto):
        try:
            idCombinadoStaffNoAdmin = f"STF##{generar_id}"
            idCombinadoStaffAdmin = f"ADSTF##{generar_id}"
            if esAdmin == True and esStaff == True:
                usuarioStaff=Usuario(id=idCombinadoStaffAdmin, nombre=nombre,apellido=apellido, password=password, 
                edad=edad, correo=correo, esAdmin=esAdmin,
                esStaff=esStaff,contacto=contacto)
                if usuarioStaff.full_clean():
                    raise ValidationError("No pueden haber espacios vacios o nulos")
                usuarioStaff.save()
                return usuarioStaff
            elif esAdmin == False and esStaff == True:
                usuarioStaff=Usuario(id=idCombinadoStaffNoAdmin, nombre=nombre,apellido=apellido, password=password,
                edad=edad, correo=correo, esAdmin=esAdmin, 
                esStaff=esStaff, contacto=contacto)
                if usuarioStaff.full_clean():
                    raise ValidationError("No pueden haber vacios o nulos")
                usuarioStaff.save()
                return usuarioStaff
        except IntegrityError as e:
            print(f"Error fatal(Creacion de staff): {e}")

    @staticmethod
    def crearUsuarioComun(nombre, apellido, password, edad, correo, contacto):
        try:
            idCombinado=f"USR##{generar_id}"
            usuarioComun=Usuario(id=idCombinado, nombre=nombre, apellido=apellido, password=password, 
            edad=edad, correo=correo, contacto=contacto)
            if usuarioComun.full_clean():
                raise ValidationError("No pueden haber ampos vacios o nulos")
            usuarioComun.save()
            return usuarioComun
        except IntegrityError as e:
            print(f"Error fatal(Crear usuario comun): {e}")



            