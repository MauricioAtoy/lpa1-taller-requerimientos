# TODO: desarrollar el sistema

import statistics
from datetime import datetime

class Hotel :
    def __init__(self, nombre, direccion, telefono, email, coordenadas, servicios, Estado):
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.email = email
        self.coordenadas = coordenadas
        self.servicios = servicios
        self.Estado = Estado
        self.ofertas = []
        self.politica_cancelacion = None

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
    
    def agregar_oferta(self, oferta):
        self.ofertas.append(oferta)

    def definir_politica(self, politica):
        self.politica_cancelacion = politica

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
        self.calificaciones = []

    def calificacion_hab (self, calificacion):
        self.calificaciones.append(calificacion)
    
    def promedio_calificacion(self):
        if not self.calificaciones:
            return 0
        return sum(self.calificaciones) / len(self.calificaciones)
        
class cliente :
    def __init__(self, nombre, num_telefono, correo_electronico, direccion):
        self.nombre = nombre
        self.num_telefono = num_telefono
        self.correo_electronico = correo_electronico
        self.direccion = direccion
        self.calificaciones = [] self.calificaciones
        
    def calificar_hab (self,habitacion, calificacion):
        self.calificaciones.append(calificacion)
        habitacion.agregar_calificacion(calificacion)

        
class Reserva:
    def __init__(self, cliente, habitacion, fecha_inicio, fecha_fin, oferta=None):
        self.cliente = cliente
        self.habitacion = habitacion
        self.fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        self.fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
        self.pagada = False
        self.total = self.calcular_total()
        self.oferta = oferta
        self.total = self.calcular_total()

    def calcular_total(self):
        dias = (self.fecha_fin - self.fecha_inicio).days
        return dias * self.habitacion.precio

    def confirmar_pago(self):
        self.pagada = True
        print("Pago confirmado")

    def generar_comprobante(self):
        if not self.pagada:
            return "Reserva no pagada"

        return f"""
        ===== COMPROBANTE =====
        Cliente: {self.cliente.nombre}
        Habitación: {self.habitacion.tipo} (#{self.habitacion.numero})
        Desde: {self.fecha_inicio.date()}
        Hasta: {self.fecha_fin.date()}
        Total pagado: ${self.total}
        =======================
        """
    def calcular_total(self):
        dias = (self.fecha_fin - self.fecha_inicio).days
        total = dias * self.habitacion.precio

        if self.oferta:
            total = self.oferta.aplicar_descuento(total)

        return total
    
    def cancelar_reserva(self, politica):
        hoy = datetime.now()
        dias_antes = (self.fecha_inicio - hoy).days

        if dias_antes >= politica.dias_anticipacion:
            if politica.reembolso:
                print("Reembolso completo")
            else:
                print("No hay reembolso")
        else:
            penalidad = self.total * politica.penalidad
            print(f" Cancelación tardía. Penalidad: ${penalidad}")
    
class Oferta:
    def __init__(self, nombre, descuento, descripcion):
        self.nombre = nombre
        self.descuento = descuento 
        self.descripcion = descripcion

    def aplicar_descuento(self, precio):
        return precio - (precio * self.descuento)

class PoliticaCancelacion:
    def __init__(self, dias_anticipacion, reembolso, penalidad):
        self.dias_anticipacion = dias_anticipacion
        self.reembolso = reembolso
        self.penalidad = penalidad       