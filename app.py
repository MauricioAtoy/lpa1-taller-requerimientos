# TODO: desarrollar el sistema

import statistics

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
    def calificar_hotel(self, calificacionH):
            self.calificacionH = calificacionH
            return statistics.mean(self.calificacionH)
        
class Habitacion :
    def __init__(self, numero, tipo, precio, estado, descripcion, servicios_hab, capacidad, fotos):
        self.numero = numero
        self.tipo = tipo
        self.precio = precio
        self.estado = estado
        self.descripcion = descripcion
        self.servicios_hab = servicios_hab
        self.capacidad = capacidad
        self.fotos = fotos
        
    def calificacion_hab (self,)
        
        pass
        
class cliente :
    def __init__(self, nombre, num_telefono, correo_electronico, direccion):
        self.nombre = nombre
        self.num_telefono = num_telefono
        self.correo_electronico = correo_electronico
        self.direccion = direccion
        self.calificaciones = [] self.calificaciones
        
    def calificar_hab (self,habitacion, calificacion):
        self.calificaciones.append(calificacion)
        habitacion.agregar_calificaion(calificacion)
    
        
        
        pass
        

        