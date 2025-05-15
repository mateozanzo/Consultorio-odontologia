# === IMPORTACIONES ===
from datetime import datetime
import json
import os

# === ARCHIVO JSON ===
ARCHIVO_JSON = "datos_consultorio.json"

# === FUNCIONES ===
def guardar_datos():
    datos = {
        "nombres_turnos": nombres_turnos,
        "numeros_socios": numeros_socios,
        "horarios": [h.strftime("%d/%m/%Y %H:%M") for h in horarios],
        "tratamientos_turno": tratamientos_turno,
        "id_doctor": id_doctor,
        "nombres_doctor": nombres_doctor,
        "apellidos_doctor": apellidos_doctor,
        "tratamientos_doctor": tratamientos_doctor
    }
    with open(ARCHIVO_JSON, "w") as f:
        json.dump(datos, f, indent=4)

def cargar_datos():
    if not os.path.exists(ARCHIVO_JSON):
        return
    with open(ARCHIVO_JSON, "r") as f:
        datos = json.load(f)
        
        nombres_turnos.extend(datos["turnos"]["nombres"])
        numeros_socios.extend(datos["turnos"]["numeros_socios"])
        horarios.extend([datetime.strptime(h, "%d/%m/%Y %H:%M") for h in datos["turnos"]["horarios"]])
        tratamientos_turno.extend([tuple(t) for t in datos["turnos"]["tratamientos"]])
        id_doctor.extend(datos["turnos"]["doctor_asignado"])
        nombres_doctor.extend(datos["doctores"]["nombres"])
        apellidos_doctor.extend(datos["doctores"]["apellidos"])
        tratamientos_doctor.extend(datos["doctores"]["tratamientos"])

def login(usuarios):
    print("=== INICIO DE SESI\u00d3N ===")
    usuario = input("Usuario: ")
    clave = input("Contrase\u00f1a: ")
    if usuario in usuarios and usuarios[usuario]["clave"] == clave:
        print("Acceso Permitido.\nBienvenido a DentalClare!\n")
        return usuario, usuarios[usuario]["perfil"]
    else:
        print("Usuario o contrase\u00f1a incorrectos.")
        return None, None

def menu(perfil):
    opciones = {
        "admin": ["1. Ingresar turnos", "2. Ver turnos", "3. Eliminar turnos", "4. Agregar doctor", "5. Eliminar doctor", "6. Mostrar doctores", "7. Salir"],
        "paciente": ["1. Ingresar turnos", "2. Ver turnos", "3. Eliminar turnos", "7. Salir"],
        "medico": ["2. Ver turnos asignados", "7. Salir"]
    }
    menu_items = ["Men\u00fa del sistema"] + opciones[perfil]
    max_largo = max(len(linea) for linea in menu_items)
    ancho_total = max_largo + 7
    print("\n" + "#" * ancho_total)
    for linea in menu_items:
        print("#  " + linea.ljust(max_largo) + "  #")
    print("#" * ancho_total)
    try:
        return int(input("\nIngrese opci\u00f3n: "))
    except ValueError:
        return menu(perfil)

def ingresar_turnos():
    if len(nombres_turnos) >= TURNOS_MAXIMOS:
        return "No hay turnos disponibles."
    numero_socio = int(input("Ingrese n\u00famero de socio: "))
    if numero_socio in numeros_socios:
        return "El socio ya tiene un turno."
    nombre = input("Nombre y apellido: ")
    horario = ingresar_horario()
    tratamiento = ingresar_tratamiento()
    doctor_asignado = None
    for i in range(len(tratamientos_doctor)):
        if TRATAMIENTOS[tratamientos_doctor[i]] == tratamiento:
            doctor_asignado = f"{nombres_doctor[i]} {apellidos_doctor[i]} (ID: {id_doctor[i]})"
            break
    if not doctor_asignado:
        return "No hay doctores disponibles para ese tratamiento."
    nombres_turnos.append(nombre)
    numeros_socios.append(numero_socio)
    horarios.append(horario)
    tratamientos_turno.append((tratamiento, doctor_asignado))
    return f"Turno registrado. Doctor asignado: {doctor_asignado}"

def mostrar_turnos(usuario, perfil):
    if not nombres_turnos:
        return "No hay turnos registrados."
    turnos = list(zip(horarios, nombres_turnos, numeros_socios, tratamientos_turno))
    turnos.sort()
    for i, (horario, nombre, socio, (tratamiento, doctor)) in enumerate(turnos, 1):
        if perfil == "medico" and usuario.split("@")[0] not in doctor:
            continue
        print(f"{i}. {nombre} - Socio: {socio} - Horario: {horario.strftime('%d/%m/%Y %H:%M')} - Tratamiento: {tratamiento} - Doctor: {doctor}")
    return "Turnos listados."

def eliminar_turno():
    mostrar_turnos(usuario_actual, perfil_actual)
    idx = int(input("N\u00famero de turno a eliminar: ")) - 1
    if 0 <= idx < len(nombres_turnos):
        nombres_turnos.pop(idx)
        numeros_socios.pop(idx)
        horarios.pop(idx)
        tratamientos_turno.pop(idx)
        return "Turno eliminado."
    return "N\u00famero de turno inv\u00e1lido."

def agregar_doctor():
    id_ = input("ID del doctor: ")
    nombre = input("Nombre: ")
    apellido = input("Apellido: ")
    for i, t in enumerate(TRATAMIENTOS):
        print(f"{i+1}. {t}")
    idx = int(input("Seleccione tratamiento: ")) - 1
    id_doctor.append(id_)
    nombres_doctor.append(nombre)
    apellidos_doctor.append(apellido)
    tratamientos_doctor.append(idx)
    return "Doctor agregado."

def eliminar_doctor():
    id_ = input("ID del doctor a eliminar: ")
    if id_ in id_doctor:
        idx = id_doctor.index(id_)
        id_doctor.pop(idx)
        nombres_doctor.pop(idx)
        apellidos_doctor.pop(idx)
        tratamientos_doctor.pop(idx)
        return "Doctor eliminado."
    return "ID no encontrado."

def mostrar_doctores():
    for i in range(len(id_doctor)):
        t = TRATAMIENTOS[tratamientos_doctor[i]]
        print(f"{i+1}. {nombres_doctor[i]} {apellidos_doctor[i]} - ID: {id_doctor[i]} - Tratamiento: {t}")
    return "Fin de la lista."

def ingresar_tratamiento():
    for i, t in enumerate(TRATAMIENTOS, 1):
        print(f"{i}. {t}")
    opcion = int(input("Seleccione opci\u00f3n: "))
    return TRATAMIENTOS[opcion - 1]

def ingresar_horario():
    while True:
        entrada = input("Fecha y hora (dd/mm/aaaa HH:MM): ")
        try:
            horario = datetime.strptime(entrada, "%d/%m/%Y %H:%M")
            if horario.weekday() == 6 or horario.hour < APERTURA or horario.hour >= CIERRE:
                print("Horario fuera de atenci\u00f3n.")
                continue
            if horario in horarios:
                print("Ese horario ya est\u00e1 ocupado.")
                continue
            return horario
        except ValueError:
            print("Formato inv\u00e1lido.")

# === CONSTANTES Y VARIABLES ===
USUARIOS = {
    "DentalClare": {"clave": "2025", "perfil": "admin"},
    "msaafigueroa@dentalclare.com": {"clave": "1234", "perfil": "medico"},
    "mzanzottera@gmail.com": {"clave": "4789", "perfil": "paciente"},
}
TRATAMIENTOS = ['Control', 'Arreglo de caries', 'Ortodoncia', 'Extracci\u00f3n']
TURNOS_MAXIMOS = 23
APERTURA = 8
CIERRE = 20

nombres_turnos = []
numeros_socios = []
horarios = []
tratamientos_turno = []
id_doctor = []
nombres_doctor = []
apellidos_doctor = []
tratamientos_doctor = []

# === PROGRAMA PRINCIPAL ===
cargar_datos()
intentos = 3
usuario_actual = None
perfil_actual = None
while intentos > 0:
    usuario_actual, perfil_actual = login(USUARIOS)
    if usuario_actual:
        break
    intentos -= 1
if not usuario_actual:
    exit()

while True:
    opcion = menu(perfil_actual)
    if opcion == 7:
        guardar_datos()
        print("\nPrograma finalizado por el usuario.")
        break
    if perfil_actual == "admin":
        acciones = [ingresar_turnos, lambda: mostrar_turnos(usuario_actual, perfil_actual), eliminar_turno, agregar_doctor, eliminar_doctor, mostrar_doctores]
    elif perfil_actual == "paciente":
        acciones = [ingresar_turnos, lambda: mostrar_turnos(usuario_actual, perfil_actual), eliminar_turno]
    elif perfil_actual == "medico":
        acciones = [None, lambda: mostrar_turnos(usuario_actual, perfil_actual)]
    try:
        funcion = acciones[opcion - 1]
        if funcion:
            resultado = funcion()
            print(resultado)
        else:
            print("Opci\u00f3n no permitida para este perfil.")
    except (IndexError, ValueError):
        print("Opci\u00f3n inv\u00e1lida.")
