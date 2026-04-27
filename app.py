# Sistema de Agencia de Viajes
import statistics
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.rule import Rule
from rich import box

console = Console()

# ─────────────────────────────────────────────────────────────
# TARIFAS (del README)
# ─────────────────────────────────────────────────────────────

TARIFAS = {
    "Aruba":   {"pasaje": 418,  "silver": 134, "gold": 167, "platinum": 191, "foto": "static/aruba.png"},
    "Bahamas": {"pasaje": 423,  "silver": 112, "gold": 183, "platinum": 202, "foto": "static/bahamas.png"},
    "Cancún":  {"pasaje": 350,  "silver": 105, "gold": 142, "platinum": 187, "foto": "static/cancun.png"},
    "Hawaii":  {"pasaje": 858,  "silver": 210, "gold": 247, "platinum": 291, "foto": "static/hawaii.png"},
    "Jamaica": {"pasaje": 380,  "silver": 115, "gold": 134, "platinum": 161, "foto": "static/jamaica.png"},
    "Madrid":  {"pasaje": 496,  "silver": 190, "gold": 230, "platinum": 270, "foto": "static/madrid.png"},
    "Miami":   {"pasaje": 334,  "silver": 122, "gold": 151, "platinum": 183, "foto": "static/miami.png"},
    "Moscu":   {"pasaje": 634,  "silver": 131, "gold": 153, "platinum": 167, "foto": "static/moscu.png"},
    "NewYork": {"pasaje": 495,  "silver": 104, "gold": 112, "platinum": 210, "foto": "static/newyork.png"},
    "Panamá":  {"pasaje": 315,  "silver": 119, "gold": 138, "platinum": 175, "foto": "static/panama.png"},
    "Paris":   {"pasaje": 512,  "silver": 210, "gold": 260, "platinum": 290, "foto": "static/paris.png"},
    "Rome":    {"pasaje": 478,  "silver": 184, "gold": 220, "platinum": 250, "foto": "static/rome.png"},
    "Seul":    {"pasaje": 967,  "silver": 205, "gold": 245, "platinum": 265, "foto": "static/seul.png"},
    "Sidney":  {"pasaje": 1045, "silver": 170, "gold": 199, "platinum": 230, "foto": "static/sidney.png"},
    "Taipei":  {"pasaje": 912,  "silver": 220, "gold": 245, "platinum": 298, "foto": "static/taipei.png"},
    "Tokio":   {"pasaje": 989,  "silver": 189, "gold": 231, "platinum": 255, "foto": "static/tokio.png"},
}

TIPOS_HAB = {
    "silver":   {
        "nombre": "Silver", "emoji": "🥈",
        "capacidad": 2,
        "descripcion": "Habitación confortable con todos los servicios básicos. Perfecta para viajeros que buscan comodidad a buen precio.",
        "servicios": ["WiFi", "TV", "Aire acondicionado", "Desayuno continental"],
    },
    "gold":     {
        "nombre": "Gold", "emoji": "🥇",
        "capacidad": 2,
        "descripcion": "Habitación superior con acabados de lujo, minibar y vista panorámica. Ideal para parejas o viajes de negocios.",
        "servicios": ["WiFi Premium", "TV 4K", "Aire acondicionado", "Desayuno buffet", "Minibar", "Caja fuerte"],
    },
    "platinum": {
        "nombre": "Platinum", "emoji": "💎",
        "capacidad": 4,
        "descripcion": "Suite de lujo con terraza privada, jacuzzi y atención personalizada. La experiencia más exclusiva del destino.",
        "servicios": ["WiFi Premium", "TV 4K", "Jacuzzi", "Desayuno buffet", "Minibar",
                      "Servicio a la habitación 24h", "Terraza privada", "Traslado aeropuerto"],
    },
}


# ─────────────────────────────────────────────────────────────
# MODELOS
# ─────────────────────────────────────────────────────────────

class PoliticaCancelacion:
    def __init__(self, nombre, dias_anticipacion, reembolso, penalidad, descripcion=""):
        self.nombre = nombre
        self.dias_anticipacion = dias_anticipacion
        self.reembolso = reembolso      # bool
        self.penalidad = penalidad      # fracción 0.0–1.0
        self.descripcion = descripcion

    def evaluar(self, fecha_inicio, total):
        dias_antes = (fecha_inicio - datetime.now()).days
        if dias_antes >= self.dias_anticipacion:
            if self.reembolso:
                return "✅ Reembolso completo aplicado.", 0
            else:
                return "❌ Cancelación sin reembolso.", total
        monto = round(total * self.penalidad, 2)
        return f"⚠  Cancelación tardía. Penalidad: ${monto:.2f}", monto

    def __str__(self):
        r = "Sí" if self.reembolso else "No"
        return (f"{self.nombre} — {self.dias_anticipacion}d anticipación | "
                f"Reembolso: {r} | Penalidad: {int(self.penalidad*100)}%")


class Oferta:
    def __init__(self, nombre, descuento, descripcion, temporada="Todo el año"):
        self.nombre = nombre
        self.descuento = descuento      # fracción 0.0–1.0
        self.descripcion = descripcion
        self.temporada = temporada

    def aplicar(self, precio):
        return round(precio * (1 - self.descuento), 2)

    def __str__(self):
        return f"{self.nombre} ({int(self.descuento*100)}% dto.) — {self.descripcion}"


class Habitacion:
    def __init__(self, tipo, destino, precio_noche, estado="Activo", politica=None):
        self.tipo = tipo                # "silver" | "gold" | "platinum"
        self.destino = destino
        self.precio_noche = precio_noche
        self.estado = estado            # "Activo" | "Inactivo"
        self.politica = politica
        self.calificaciones = []        # [{"puntaje": n, "comentario": "..."}]

    @property
    def nombre_tipo(self):
        return TIPOS_HAB[self.tipo]["nombre"]

    @property
    def emoji(self):
        return TIPOS_HAB[self.tipo]["emoji"]

    @property
    def servicios(self):
        return TIPOS_HAB[self.tipo]["servicios"]

    @property
    def capacidad(self):
        return TIPOS_HAB[self.tipo]["capacidad"]

    @property
    def descripcion(self):
        return TIPOS_HAB[self.tipo]["descripcion"]

    @property
    def foto(self):
        return TARIFAS[self.destino]["foto"]

    def agregar_calificacion(self, puntaje, comentario=""):
        self.calificaciones.append({"puntaje": puntaje, "comentario": comentario})

    def promedio(self):
        if not self.calificaciones:
            return 0.0
        return round(statistics.mean(c["puntaje"] for c in self.calificaciones), 2)

    def estrellas(self):
        p = int(self.promedio())
        return "★" * p + "☆" * (5 - p)

    def disponible(self):
        return self.estado == "Activo"

    def __str__(self):
        return f"{self.emoji} {self.nombre_tipo} en {self.destino} — ${self.precio_noche}/noche"


class Hotel:
    def __init__(self, nombre, direccion, telefono, email, coordenadas, servicios, estado="Activo"):
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.email = email
        self.coordenadas = coordenadas
        self.servicios = servicios
        self.servicios_adicionales = []
        self.galeria = []
        self.estado = estado
        self.habitaciones = []
        self.ofertas = []
        self.politica_global = None

    def calificacion_general(self):
        promedios = [h.promedio() for h in self.habitaciones if h.calificaciones]
        return round(statistics.mean(promedios), 2) if promedios else 0.0

    def estrellas_general(self):
        p = int(self.calificacion_general())
        return "★" * p + "☆" * (5 - p)

    def habitaciones_destino(self, destino):
        return [h for h in self.habitaciones if h.destino == destino and h.disponible()]

    def agregar_oferta(self, o):
        self.ofertas.append(o)

    def agregar_habitacion(self, h):
        self.habitaciones.append(h)


class Cliente:
    def __init__(self, nombre, telefono, email, direccion):
        self.nombre = nombre
        self.telefono = telefono
        self.email = email
        self.direccion = direccion
        self.reservas = []

    def __str__(self):
        return f"{self.nombre} | {self.email} | {self.telefono}"


class Reserva:
    _contador = 1

    def __init__(self, cliente, habitacion, fecha_inicio, fecha_fin, num_pasajeros=1, oferta=None):
        self.id = Reserva._contador
        Reserva._contador += 1
        self.cliente = cliente
        self.habitacion = habitacion
        self.fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        self.fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
        self.num_pasajeros = num_pasajeros
        self.oferta = oferta
        self.pagada = False
        self.cancelada = False
        self.total = self._calcular_total()

    def _calcular_total(self):
        dias = (self.fecha_fin - self.fecha_inicio).days
        if dias <= 0:
            return 0.0
        tarifa = TARIFAS[self.habitacion.destino]
        total = tarifa["pasaje"] * self.num_pasajeros + self.habitacion.precio_noche * dias
        if self.oferta:
            total = self.oferta.aplicar(total)
        return round(total, 2)

    def confirmar_pago(self):
        self.pagada = True

    def cancelar(self):
        pol = self.habitacion.politica
        if not pol:
            self.cancelada = True
            return "Reserva cancelada. Sin política definida, sin penalidad."
        msg, _ = pol.evaluar(self.fecha_inicio, self.total)
        self.cancelada = True
        return msg

    def comprobante(self):
        if not self.pagada:
            return "⚠  La reserva aún no ha sido pagada."
        dias = (self.fecha_fin - self.fecha_inicio).days
        tarifa = TARIFAS[self.habitacion.destino]
        pasajes   = tarifa["pasaje"] * self.num_pasajeros
        hab_costo = self.habitacion.precio_noche * dias
        oferta_str = (f"\n  Oferta aplicada : {self.oferta.nombre} "
                      f"(-{int(self.oferta.descuento*100)}%)" if self.oferta else "")
        return f"""
╔══════════════════════════════════════════╗
║        ✈  COMPROBANTE DE RESERVA  ✈     ║
╠══════════════════════════════════════════╣
  Reserva #       : {self.id}
  Cliente         : {self.cliente.nombre}
  Teléfono        : {self.cliente.telefono}
  Email           : {self.cliente.email}
──────────────────────────────────────────
  Destino         : {self.habitacion.destino}
  Habitación      : {self.habitacion.nombre_tipo} {self.habitacion.emoji}
  Pasajeros       : {self.num_pasajeros}
  Check-in        : {self.fecha_inicio.date()}
  Check-out       : {self.fecha_fin.date()}
  Noches          : {dias}
──────────────────────────────────────────
  Pasajes         : ${pasajes:.2f}  ({self.num_pasajeros} × ${tarifa['pasaje']})
  Habitación      : ${hab_costo:.2f}  ({dias} × ${self.habitacion.precio_noche}){oferta_str}
  ─────────────────────────────────────
  TOTAL PAGADO    : ${self.total:.2f}
╚══════════════════════════════════════════╝"""


# ─────────────────────────────────────────────────────────────
# DATOS DE EJEMPLO
# ─────────────────────────────────────────────────────────────

def crear_agencia():
    hotel = Hotel(
        nombre="Agencia Viajes Mundo",
        direccion="Calle 72 #10-45, Bogotá, Colombia",
        telefono="+57 1 800-VIAJES",
        email="reservas@viajaelmundo.co",
        coordenadas={"lat": 4.7110, "lng": -74.0721},
        servicios=["Restaurante", "Piscina", "Gimnasio", "Spa", "Bar", "WiFi gratuito"],
        estado="Activo"
    )
    hotel.servicios_adicionales = ["Estacionamiento", "Área de Coworking",
                                   "Sala de Conferencias", "Lavandería"]
    hotel.galeria = ["static/aruba.png", "static/hawaii.png", "static/paris.png"]

    pol_flex = PoliticaCancelacion("Flexible", 3,  True,  0.00,
        "Cancela gratis hasta 3 días antes del check-in.")
    pol_mod  = PoliticaCancelacion("Moderada", 7,  True,  0.50,
        "Reembolso del 50% si cancelas con 7+ días de anticipación.")
    pol_est  = PoliticaCancelacion("Estricta", 14, False, 1.00,
        "Sin reembolso. Solo modificación con 14+ días de anticipación.")
    hotel.politica_global = pol_flex

    hotel.agregar_oferta(Oferta("Temporada Baja",    0.20, "20% de descuento en temporada baja.", "Marzo – Junio"))
    hotel.agregar_oferta(Oferta("Luna de Miel",      0.10, "10% dto. + cena romántica incluida.", "Todo el año"))
    hotel.agregar_oferta(Oferta("Paquete Familia",   0.15, "15% dto. + actividades para niños.",  "Julio – Agosto"))
    hotel.agregar_oferta(Oferta("Reserva Anticipada",0.12, "12% dto. reservando con 60+ días.",   "Todo el año"))

    califs_ejemplo = {
        "Aruba":   [(5,"Paraíso total"),(4,"Playa increíble")],
        "Bahamas": [(5,"Aguas cristalinas"),(5,"Lujo total")],
        "Cancún":  [(4,"Muy buen hotel"),(3,"Ruidoso en Semana Santa")],
        "Hawaii":  [(5,"Naturaleza impresionante"),(5,"Inolvidable")],
        "Jamaica": [(4,"Muy relajado"),(5,"Comida exquisita")],
        "Madrid":  [(5,"Ciudad mágica"),(4,"Fácil transporte")],
        "Miami":   [(4,"Playa y nightlife"),(4,"Ideal para compras")],
        "Moscu":   [(3,"Muy frío en invierno"),(4,"Arquitectura increíble")],
        "NewYork": [(5,"La ciudad que nunca duerme"),(4,"Muy caro pero vale")],
        "Panamá":  [(4,"Muy accesible"),(5,"Canal impresionante")],
        "Paris":   [(5,"Romántico"),(5,"Gastronomía top")],
        "Rome":    [(5,"Historia viva"),(4,"Comida deliciosa")],
        "Seul":    [(5,"Tecnología y cultura"),(4,"K-food riquísima")],
        "Sidney":  [(4,"Opera House increíble"),(5,"Gente muy amable")],
        "Taipei":  [(4,"Street food increíble"),(5,"Ciudad muy limpia")],
        "Tokio":   [(5,"Experiencia única"),(5,"Organización perfecta")],
    }

    politicas = {"silver": pol_flex, "gold": pol_mod, "platinum": pol_est}

    for destino, tarifa in TARIFAS.items():
        for tipo in ["silver", "gold", "platinum"]:
            hab = Habitacion(tipo, destino, tarifa[tipo],
                             estado="Activo", politica=politicas[tipo])
            for puntaje, comentario in califs_ejemplo.get(destino, []):
                hab.agregar_calificacion(puntaje, comentario)
            hotel.agregar_habitacion(hab)

    return hotel


# ─────────────────────────────────────────────────────────────
# ESTADO GLOBAL
# ─────────────────────────────────────────────────────────────

hotel = crear_agencia()
clientes_registrados = []
reservas_globales = []


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def banner():
    cal = hotel.calificacion_general()
    est = hotel.estrellas_general()
    color = "green" if hotel.estado == "Activo" else "red"
    console.print()
    console.print(Panel.fit(
        f"[bold yellow]✈  {hotel.nombre}[/bold yellow]\n"
        f"[dim]{hotel.direccion}[/dim]\n"
        f"[cyan]📞 {hotel.telefono}[/cyan]   [cyan]✉  {hotel.email}[/cyan]\n"
        f"Estado: [{color}]{hotel.estado}[/{color}]   "
        f"Calificación: [yellow]{est}[/yellow] ({cal}/5.0)",
        border_style="yellow",
        title="[bold white]SISTEMA DE RESERVAS — AGENCIA DE VIAJES[/bold white]"
    ))


def pausa():
    Prompt.ask("\n[dim]Presiona Enter para continuar[/dim]", default="")
    console.clear()


def pedir_cliente():
    email = Prompt.ask("Tu correo electrónico")
    for c in clientes_registrados:
        if c.email.lower() == email.lower():
            console.print(f"[green]Bienvenido/a de nuevo, {c.nombre}![/green]")
            return c
    console.print("[yellow]No estás registrado/a. Ingresa tus datos:[/yellow]")
    nombre    = Prompt.ask("Nombre completo")
    telefono  = Prompt.ask("Teléfono")
    direccion = Prompt.ask("Dirección")
    c = Cliente(nombre, telefono, email, direccion)
    clientes_registrados.append(c)
    console.print(f"[green]¡Registro exitoso! Bienvenido/a, {c.nombre}.[/green]")
    return c


# ─────────────────────────────────────────────────────────────
# VISTAS
# ─────────────────────────────────────────────────────────────

def ver_hotel():
    console.print(Rule("[bold yellow]Información de la Agencia[/bold yellow]"))

    t = Table(box=box.SIMPLE, show_header=False)
    t.add_column("", style="cyan")
    for s in hotel.servicios:
        t.add_row(f"✔  {s}")
    console.print(Panel(t, title="Servicios del hotel"))

    t2 = Table(box=box.SIMPLE, show_header=False)
    t2.add_column("", style="magenta")
    for s in hotel.servicios_adicionales:
        t2.add_row(f"➕ {s}")
    console.print(Panel(t2, title="Servicios adicionales"))

    console.print(Panel(
        "\n".join(f"🖼  {f}" for f in hotel.galeria),
        title="Galería de fotos"
    ))
    console.print(f"[dim]Coordenadas: {hotel.coordenadas}[/dim]")


def ver_tarifas():
    console.print(Rule("[bold cyan]Tarifas por Destino[/bold cyan]"))
    t = Table(box=box.ROUNDED, show_lines=True)
    t.add_column("Destino",           style="bold")
    t.add_column("✈ Pasaje",          justify="right", style="cyan")
    t.add_column("🥈 Silver/noche",   justify="right")
    t.add_column("🥇 Gold/noche",     justify="right", style="yellow")
    t.add_column("💎 Platinum/noche", justify="right", style="magenta")
    t.add_column("⭐ Calif.",          justify="center")

    for destino, tarifa in TARIFAS.items():
        habs = [h for h in hotel.habitaciones if h.destino == destino and h.calificaciones]
        promedios = [h.promedio() for h in habs]
        cal = round(statistics.mean(promedios), 1) if promedios else 0.0
        cal_str = (f"[yellow]{'★'*int(cal)}{'☆'*(5-int(cal))}[/yellow] ({cal})"
                   if cal > 0 else "[dim]Sin cal.[/dim]")
        t.add_row(destino,
                  f"${tarifa['pasaje']}",
                  f"${tarifa['silver']}",
                  f"${tarifa['gold']}",
                  f"${tarifa['platinum']}",
                  cal_str)
    console.print(t)
    console.print("[dim]* Pasaje = por persona (ida y vuelta). Habitación = por noche.[/dim]")


def ver_ofertas():
    console.print(Rule("[bold green]Ofertas y Promociones[/bold green]"))
    t = Table(box=box.ROUNDED, show_lines=True)
    t.add_column("#",         style="dim", width=3)
    t.add_column("Oferta",   style="bold green")
    t.add_column("Dto.",      justify="center", style="yellow")
    t.add_column("Temporada", style="cyan")
    t.add_column("Descripción")
    for i, o in enumerate(hotel.ofertas, 1):
        t.add_row(str(i), o.nombre, f"{int(o.descuento*100)}%", o.temporada, o.descripcion)
    console.print(t)


def ver_politicas():
    console.print(Rule("[bold red]Condiciones de Pago y Cancelación[/bold red]"))
    console.print(Panel(
        "[bold]🥈 Silver → Política Flexible:[/bold]\n"
        "   Cancela gratis hasta 3 días antes del check-in. Reembolso completo.\n\n"
        "[bold]🥇 Gold → Política Moderada:[/bold]\n"
        "   Cancela con 7+ días: reembolso del 50%. Después: sin reembolso.\n\n"
        "[bold]💎 Platinum → Política Estricta:[/bold]\n"
        "   Sin reembolso. Solo modificación con 14+ días de anticipación.\n\n"
        "💳 [bold]Formas de pago:[/bold] Tarjeta crédito/débito, transferencia bancaria.\n"
        "🔄 [bold]Reembolsos:[/bold] Procesados en 5–10 días hábiles.\n"
        "✏  [bold]Modificaciones:[/bold] Sujetas a disponibilidad y política aplicable.",
        title="Políticas de Cancelación y Pago", border_style="red"
    ))


def ver_detalle_destino(destino):
    console.print(Rule(f"[bold cyan]{destino}[/bold cyan]"))
    console.print(f"[dim]📷 Foto: {TARIFAS[destino]['foto']}[/dim]\n")

    for tipo in ["silver", "gold", "platinum"]:
        habs = [h for h in hotel.habitaciones if h.destino == destino and h.tipo == tipo]
        if not habs:
            continue
        h = habs[0]
        color = {"silver": "white", "gold": "yellow", "platinum": "magenta"}[tipo]
        estado_c = "green" if h.disponible() else "red"
        servicios_str = "  ".join(f"✔ {s}" for s in h.servicios)
        cal_str = f"{h.estrellas()} ({h.promedio()}/5)" if h.calificaciones else "Sin calificar aún"

        console.print(Panel(
            f"[bold]{h.emoji} {h.nombre_tipo}[/bold]  —  ${h.precio_noche}/noche   "
            f"[{estado_c}]{h.estado}[/{estado_c}]   👥 Hasta {h.capacidad} personas\n\n"
            f"{h.descripcion}\n\n"
            f"[bold]Servicios:[/bold] {servicios_str}\n\n"
            f"[yellow]⭐ Calificación: {cal_str}[/yellow]",
            border_style=color
        ))

        if h.calificaciones:
            for c in h.calificaciones:
                stars = "★" * c["puntaje"] + "☆" * (5 - c["puntaje"])
                console.print(f"   [yellow]{stars}[/yellow]  {c.get('comentario','')}")
        console.print()


def buscar_destinos():
    console.print(Rule("[bold]Buscar Destinos[/bold]"))
    console.print("[dim]Presiona Enter para omitir cualquier filtro[/dim]\n")

    pasaje_max_s = Prompt.ask("Pasaje máximo por persona ($)", default="")
    hab_max_s    = Prompt.ask("Precio máximo habitación/noche ($)", default="")
    tipo_s       = Prompt.ask("Tipo [silver / gold / platinum]", default="")
    cal_min_s    = Prompt.ask("Calificación mínima (1-5)", default="")

    pasaje_max = float(pasaje_max_s) if pasaje_max_s else None
    hab_max    = float(hab_max_s)    if hab_max_s    else None
    tipo_fil   = tipo_s.lower()      if tipo_s.lower() in TIPOS_HAB else None
    cal_min    = float(cal_min_s)    if cal_min_s    else None

    resultados = []
    for destino, tarifa in TARIFAS.items():
        if pasaje_max and tarifa["pasaje"] > pasaje_max:
            continue
        tipos = [tipo_fil] if tipo_fil else list(TIPOS_HAB.keys())
        for tipo in tipos:
            if hab_max and tarifa[tipo] > hab_max:
                continue
            habs = [h for h in hotel.habitaciones
                    if h.destino == destino and h.tipo == tipo and h.disponible()]
            if not habs:
                continue
            h = habs[0]
            if cal_min and h.promedio() < cal_min:
                continue
            resultados.append((destino, h))

    if not resultados:
        console.print("[yellow]No se encontraron destinos con esos criterios.[/yellow]")
        return

    t = Table(box=box.ROUNDED, show_lines=True)
    t.add_column("Destino",     style="bold")
    t.add_column("Tipo",        style="bold")
    t.add_column("✈ Pasaje",   justify="right", style="cyan")
    t.add_column("🏨 Hab/noche", justify="right", style="green")
    t.add_column("Calificación")

    for destino, h in resultados:
        cal_str = f"{h.estrellas()} ({h.promedio()})" if h.calificaciones else "Sin cal."
        t.add_row(destino,
                  f"{h.emoji} {h.nombre_tipo}",
                  f"${TARIFAS[destino]['pasaje']}",
                  f"${h.precio_noche}",
                  f"[yellow]{cal_str}[/yellow]")
    console.print(t)


def hacer_reserva():
    console.print(Rule("[bold green]Nueva Reserva[/bold green]"))

    # 1. Cliente
    cliente = pedir_cliente()

    # 2. Elegir destino
    ver_tarifas()
    destinos_lista = list(TARIFAS.keys())
    console.print()
    for i, d in enumerate(destinos_lista, 1):
        console.print(f"  [cyan]{i:2}.[/cyan] {d}")
    idx = IntPrompt.ask(f"\nElige destino (1-{len(destinos_lista)})")
    if not 1 <= idx <= len(destinos_lista):
        console.print("[red]Opción inválida.[/red]")
        return
    destino = destinos_lista[idx - 1]

    # 3. Tipo de habitación — mostrar detalle primero
    ver_detalle_destino(destino)
    tipo = Prompt.ask("Tipo de habitación", choices=["silver", "gold", "platinum"])

    habs = [h for h in hotel.habitaciones
            if h.destino == destino and h.tipo == tipo and h.disponible()]
    if not habs:
        console.print("[red]No hay habitaciones disponibles para esa opción.[/red]")
        return
    habitacion = habs[0]

    # 4. Fechas y pasajeros
    console.print("[dim]Formato: YYYY-MM-DD  (ej. 2025-12-20)[/dim]")
    fecha_ini = Prompt.ask("Check-in")
    fecha_fin = Prompt.ask("Check-out")
    try:
        fi = datetime.strptime(fecha_ini, "%Y-%m-%d")
        ff = datetime.strptime(fecha_fin, "%Y-%m-%d")
        if ff <= fi:
            console.print("[red]La fecha de salida debe ser posterior a la de entrada.[/red]")
            return
    except ValueError:
        console.print("[red]Formato de fecha inválido. Usa YYYY-MM-DD.[/red]")
        return

    num_pasajeros = IntPrompt.ask(f"Número de pasajeros (1-{habitacion.capacidad})")
    if not 1 <= num_pasajeros <= habitacion.capacidad:
        console.print(f"[red]La habitación admite entre 1 y {habitacion.capacidad} pasajeros.[/red]")
        return

    # 5. Oferta opcional
    oferta = None
    ver_ofertas()
    if Confirm.ask("\n¿Deseas aplicar una oferta?", default=False):
        idx_o = IntPrompt.ask(f"Número de oferta (1-{len(hotel.ofertas)})")
        if 1 <= idx_o <= len(hotel.ofertas):
            oferta = hotel.ofertas[idx_o - 1]

    # 6. Resumen antes de confirmar
    dias = (ff - fi).days
    tarifa = TARIFAS[destino]
    pasajes   = tarifa["pasaje"] * num_pasajeros
    hab_costo = habitacion.precio_noche * dias
    subtotal  = pasajes + hab_costo
    total_fin = oferta.aplicar(subtotal) if oferta else subtotal

    console.print(Panel(
        f"Destino        : [bold]{destino}[/bold]\n"
        f"Habitación     : {habitacion.emoji} {habitacion.nombre_tipo}\n"
        f"Pasajeros      : {num_pasajeros}\n"
        f"Check-in       : {fecha_ini}\n"
        f"Check-out      : {fecha_fin}  ({dias} noche(s))\n"
        + (f"Oferta         : {oferta.nombre} (-{int(oferta.descuento*100)}%)\n" if oferta else "") +
        f"\n✈  Pasajes      : ${pasajes:.2f}  ({num_pasajeros} × ${tarifa['pasaje']})\n"
        f"🏨 Habitación   : ${hab_costo:.2f}  ({dias} × ${habitacion.precio_noche})\n"
        f"[bold green]💰 TOTAL        : ${total_fin:.2f}[/bold green]",
        title="Resumen de Reserva", border_style="green"
    ))

    if not Confirm.ask("¿Confirmar reserva?", default=True):
        console.print("[yellow]Reserva cancelada.[/yellow]")
        return

    # 7. Pago
    console.print("\n[bold]Método de pago:[/bold]")
    console.print("  [1] Tarjeta de crédito/débito")
    console.print("  [2] Transferencia bancaria")
    metodo = Prompt.ask("Método", choices=["1", "2"])

    if metodo == "1":
        Prompt.ask("Número de tarjeta", password=True)
        Prompt.ask("Vencimiento (MM/AA)")
        Prompt.ask("CVV", password=True)
    else:
        console.print(f"[cyan]Transfiere ${total_fin:.2f} a:\n"
                      f"Banco Viajes Mundo — Cta. 001-234-5678-9[/cyan]")
        Prompt.ask("Presiona Enter cuando completes la transferencia")

    # 8. Crear reserva confirmada
    reserva = Reserva(cliente, habitacion, fecha_ini, fecha_fin, num_pasajeros, oferta)
    reserva.confirmar_pago()
    cliente.reservas.append(reserva)
    reservas_globales.append(reserva)

    console.print("\n[bold green]✅ ¡Pago confirmado! Tu reserva está efectuada.[/bold green]")
    console.print(reserva.comprobante())


def mis_reservas():
    console.print(Rule("[bold]Mis Reservas[/bold]"))
    cliente = pedir_cliente()

    if not cliente.reservas:
        console.print("[yellow]No tienes reservas registradas.[/yellow]")
        return

    t = Table(box=box.ROUNDED, show_lines=True)
    t.add_column("ID",       style="dim", width=4)
    t.add_column("Destino",  style="bold")
    t.add_column("Tipo")
    t.add_column("Check-in")
    t.add_column("Check-out")
    t.add_column("Total",    style="green", justify="right")
    t.add_column("Estado")

    for r in cliente.reservas:
        if r.cancelada:
            estado = "[red]Cancelada[/red]"
        elif r.pagada:
            estado = "[green]Confirmada[/green]"
        else:
            estado = "[yellow]Pendiente[/yellow]"
        t.add_row(str(r.id), r.habitacion.destino,
                  f"{r.habitacion.emoji} {r.habitacion.nombre_tipo}",
                  str(r.fecha_inicio.date()), str(r.fecha_fin.date()),
                  f"${r.total:.2f}", estado)
    console.print(t)

    if Confirm.ask("¿Ver comprobante de alguna reserva?", default=False):
        rid = IntPrompt.ask("ID de la reserva")
        for r in cliente.reservas:
            if r.id == rid:
                console.print(r.comprobante())
                return
        console.print("[red]Reserva no encontrada.[/red]")


def calificar():
    console.print(Rule("[bold yellow]Calificar mi Estadía[/bold yellow]"))
    email = Prompt.ask("Tu correo electrónico")
    cliente = next((c for c in clientes_registrados if c.email.lower() == email.lower()), None)

    if not cliente or not cliente.reservas:
        console.print("[yellow]No se encontraron reservas para ese correo.[/yellow]")
        return

    t = Table(box=box.SIMPLE)
    t.add_column("#")
    t.add_column("Destino")
    t.add_column("Tipo")
    for i, r in enumerate(cliente.reservas, 1):
        t.add_row(str(i), r.habitacion.destino, r.habitacion.nombre_tipo)
    console.print(t)

    idx = IntPrompt.ask(f"Número de reserva a calificar (1-{len(cliente.reservas)})")
    if not 1 <= idx <= len(cliente.reservas):
        console.print("[red]Opción inválida.[/red]")
        return

    reserva = cliente.reservas[idx - 1]
    puntaje = IntPrompt.ask("Puntaje (1-5)")
    if not 1 <= puntaje <= 5:
        console.print("[red]El puntaje debe estar entre 1 y 5.[/red]")
        return
    comentario = Prompt.ask("Comentario (opcional)", default="")
    reserva.habitacion.agregar_calificacion(puntaje, comentario)
    console.print(f"[green]¡Gracias por tu calificación! "
                  f"Promedio de {reserva.habitacion.destino} {reserva.habitacion.nombre_tipo}: "
                  f"{reserva.habitacion.promedio()}/5[/green]")


# ─────────────────────────────────────────────────────────────
# MENÚ PRINCIPAL
# ─────────────────────────────────────────────────────────────

def menu():
    opciones = {
        "1": ("🏨  Información de la agencia",      ver_hotel),
        "2": ("✈  Ver tarifas y destinos",          ver_tarifas),
        "3": ("🔍  Buscar destinos (filtros)",       buscar_destinos),
        "4": ("📋  Detalle de un destino",           None),   # manejado aparte
        "5": ("🎁  Ofertas y promociones",           ver_ofertas),
        "6": ("📜  Políticas de cancelación y pago", ver_politicas),
        "7": ("📅  Hacer una reserva",               hacer_reserva),
        "8": ("🗂  Mis reservas / comprobante",      mis_reservas),
        "9": ("⭐  Calificar mi estadía",            calificar),
        "0": ("🚪  Salir",                           None),
    }

    while True:
        banner()
        t = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        t.add_column("Op", style="bold cyan", width=3)
        t.add_column("Acción")
        for k, (label, _) in opciones.items():
            t.add_row(k, label)
        console.print(Panel(t, title="[bold]MENÚ PRINCIPAL[/bold]", border_style="yellow"))

        opcion = Prompt.ask("Selecciona una opción", choices=list(opciones.keys()))

        if opcion == "0":
            console.print("\n[bold yellow]¡Hasta pronto! Buen viaje ✈[/bold yellow]\n")
            break

        console.print()
        try:
            if opcion == "4":
                destinos_lista = list(TARIFAS.keys())
                for i, d in enumerate(destinos_lista, 1):
                    console.print(f"  [cyan]{i:2}.[/cyan] {d}")
                idx = IntPrompt.ask(f"Elige destino (1-{len(destinos_lista)})")
                if 1 <= idx <= len(destinos_lista):
                    ver_detalle_destino(destinos_lista[idx - 1])
            else:
                _, fn = opciones[opcion]
                if fn:
                    fn()
        except KeyboardInterrupt:
            console.print("\n[dim]Operación cancelada.[/dim]")
        except Exception as e:
            console.print(f"[red]Error inesperado: {e}[/red]")

        pausa()



# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    console.clear()
    menu()