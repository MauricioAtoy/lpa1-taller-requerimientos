# TODO: desarrollar el sistema

class Hotel :
    def __init__(self, nombre, direccion, telefono, email, coordenadas, servicios, Estado):
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.email = email
        self.coordenadas = coordenadas
        self.servicios = servicios
        self.Estado = Estado
        
class Habitacion :
    def __init__(self, numero, tipo, precio, disponibilidad):
        self.numero = numero
        self.tipo = tipo
        self.precio = precio
        self.disponibilidad = disponibilidad
        