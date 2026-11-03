import uuid


def generar_id():
    codigoAleatorio=str(uuid.uuid4())[:6]
   
    
    return codigoAleatorio
