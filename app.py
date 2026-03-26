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
        
        def mostrar_informacion(self):
            print(f"Nombre: {self.nombre}")
            print(f"Dirección: {self.direccion}")
            print(f"Teléfono: {self.telefono}")
            print(f"Email: {self.email}")
            print(f"Coordenadas: {self.coordenadas}")
            print(f"Servicios: {', '.join(self.servicios)}")
            print(f"Estado: {self.Estado}")
            
        def actualizar_estado(self, nuevo_estado):
            self.Estado = nuevo_estado
            print(f"Estado actualizado a: {self.Estado}")
            
        def agregar_servicio(self, servicio):
            self.servicios.append(servicio)
            print(f"Servicio '{servicio}' agregado.")
        
        def eliminar_servicio(self, servicio):
            if servicio in self.servicios:
                self.servicios.remove(servicio)
                print(f"Servicio '{servicio}' eliminado.")
            else:
                print(f"Servicio '{servicio}' no encontrado.")
        def listar_servicios(self):
            print("Servicios disponibles:")
            for servicio in self.servicios:
                print(f"- {servicio}")
        def calificar_hotel(self, calificacion):
            print(f"Hotel '{self.nombre}' calificado con {calificacion} estrellas.")
        
class Habitacion (Hotel) :
    def __init__(self, numero, tipo, precio, disponibilidad):
        super().__init__(nombre="", direccion="", telefono="", email="", coordenadas=(), servicios=[], Estado="")
        self.numero = numero
        self.tipo = tipo
        self.precio = precio
        self.disponibilidad = disponibilidad
        