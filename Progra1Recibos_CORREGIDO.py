import json
import os
from datetime import datetime
USUARIOS_JSON = "usuarios.json"

def cargar_usuarios():
    if not os.path.exists(USUARIOS_JSON):
        return {}
    with open(USUARIOS_JSON, "r") as f:
        return json.load(f)

def guardar_usuarios(usuarios):
    with open(USUARIOS_JSON, "w") as f:
        json.dump(usuarios, f, indent=4)

def registrar_usuario():
    print("=== Registro de usuario ===")
    nombre = input("Nombre: ")
    apellido = input("Apellido: ")
    email = input("Email: ")
    dni = input("Documento (DNI): ")
    perfil = input("Perfil (paciente/medico): ").lower()
    while perfil=="admin":
        print("el perfil no puede ser admin")
        perfil = input("Perfil (paciente/medico): ").lower()
    if perfil not in ["paciente", "medico"]:
        print("Perfil inválido. Se asignará 'paciente' por defecto.")
        perfil = "paciente"

    usuarios = cargar_usuarios()
    if email in usuarios:
        print("Ya existe una cuenta registrada con este email.")
        return False

    while True:
        password1 = input("Contraseña (visible): ")
        password2 = input("Confirmar contraseña (visible): ")
        if password1 == password2:
            break
        print("Las contraseñas no coinciden. Intentá de nuevo.")

    usuarios[email] = {
        "nombre": nombre,
        "apellido": apellido,
        "dni": dni,
        "password": password1,
        "perfil": perfil
    }
    guardar_usuarios(usuarios)
    print("Usuario registrado correctamente.")
    return True

def login():
    print("=== Iniciar sesión ===")
    email = input("Email: ")
    password = input("Contraseña (visible): ")

    usuarios = cargar_usuarios()
    if email in usuarios and usuarios[email]["password"] == password:
        print(f"Bienvenido/a {usuarios[email]['nombre']} {usuarios[email]['apellido']}")
        perfil = usuarios[email].get("perfil", "paciente")
        return email, perfil
    print("Email o contraseña incorrectos.")
    return None, None

def menu_inicio():
    while True:
        print("\n1. Iniciar sesión")
        print("2. Registrarse")
        opcion = input("Seleccioná una opción (1 o 2): ")
        if opcion == "1":
            email, perfil = login()
            if email:
                return email, perfil
        elif opcion == "2":
            registrar_usuario()
        else:
            print("Opción inválida. Intentá de nuevo.")

ARCHIVO_JSON = "datos_consultorio.json"

TRATAMIENTOS = ['Control', 'Arreglo de caries', 'Ortodoncia', 'Extracción']
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


def guardar_datos():
    datos = {
        "turnos": {
            "nombres": nombres_turnos,
            "numeros_socios": numeros_socios,
            "horarios": [h.strftime("%d/%m/%Y %H:%M") for h in horarios],
            "tratamientos": tratamientos_turno
        },
        "doctores": {
            "id": id_doctor,
            "nombres": nombres_doctor,
            "apellidos": apellidos_doctor,
            "tratamientos": tratamientos_doctor
        }
    }
    with open(ARCHIVO_JSON, "w") as f:
        json.dump(datos, f, indent=4)

def cargar_datos():
    if not os.path.exists(ARCHIVO_JSON):
        return
    with open(ARCHIVO_JSON, "r") as f:
        datos = json.load(f)
        global nombres_turnos, numeros_socios, horarios, tratamientos_turno
        global id_doctor, nombres_doctor, apellidos_doctor, tratamientos_doctor
        nombres_turnos.extend(datos["turnos"]["nombres"])
        numeros_socios.extend(datos["turnos"]["numeros_socios"])
        horarios.extend([datetime.strptime(h, "%d/%m/%Y %H:%M") for h in datos["turnos"]["horarios"]])
        tratamientos_turno.extend([tuple(t) for t in datos["turnos"]["tratamientos"]])
        id_doctor.extend(datos["doctores"]["id"])
        nombres_doctor.extend(datos["doctores"]["nombres"])
        apellidos_doctor.extend(datos["doctores"]["apellidos"])
        tratamientos_doctor.extend(datos["doctores"]["tratamientos"])

if not id_doctor:
    id_doctor.extend(["D001", "D002", "D003"])
    nombres_doctor.extend(["Mateo", "Matias", "María"])
    apellidos_doctor.extend(["Pérez", "Gómez", "Fernández"])
    tratamientos_doctor.extend([0, 1, 2])  


def menu(perfil):
    opciones = {
        "admin": ["1. Ingresar turnos", "2. Ver turnos", "3. Mostrar agenda diaria","4. Eliminar turnos", "5. Agregar doctor", "6. Eliminar doctor", "7. Mostrar doctores", "8. Salir"],
        "paciente": ["1. Ingresar turnos", "2. Ver turnos", "3. Eliminar turnos", "4. Imprimir recibo", "8. Salir"],
        "medico": ["2. Ver turnos asignados", "3. Ver agenda diaria", "4. Imprimir recibo", "8. Salir"]
    }
    menu_items = ["Menú del sistema"] + opciones[perfil]
    max_largo = max(len(linea) for linea in menu_items)
    ancho_total = max_largo + 8
    print("\n" + "#" * ancho_total)
    for linea in menu_items:
        print("#  " + linea.ljust(max_largo) + "  #")
    print("#" * ancho_total)
    try:
        return int(input("\nIngrese opción: "))
    except ValueError:
        return menu(perfil)

def ingresar_turnos():
    if len(nombres_turnos) >= TURNOS_MAXIMOS:
        return "No hay turnos disponibles."
    j=False
    while j!=True:
        numero_socio = int(input("Ingrese número de socio del paciente: "))
        if numero_socio < 1:
            print("El número de socio no puede ser 0 o negativo.")
        elif numero_socio in numeros_socios:
            print("El número de socio ya existe, ingrese otro.")
        else:
            nombre = input("Nombre y apellido: ").strip()
            j=True
    while not nombre:
        print("El nombre no puede estar vacío.")
        nombre = input("\nIngrese nombre y apellido del paciente: ").strip()
    horario = ingresar_horario()
    tratamiento = ingresar_tratamiento()

    doctores_disponibles = []
    for i in range(len(tratamientos_doctor)):
        if TRATAMIENTOS[tratamientos_doctor[i]] == tratamiento:
            doctores_disponibles.append(i)
    
    if not doctores_disponibles:
        return "No hay doctores disponibles para ese tratamiento."
    
    print("\nDoctores disponibles para este tratamiento:")
    for i, idx in enumerate(doctores_disponibles, 1):
        doctor_nombre = f"{nombres_doctor[idx]} {apellidos_doctor[idx]} (ID: {id_doctor[idx]})"
        print(f"{i}. {doctor_nombre}")
    opcion_doctor = int(input("Seleccione el número del doctor que desea: ")) - 1
    if 0 <= opcion_doctor < len(doctores_disponibles):
        doctor_idx = doctores_disponibles[opcion_doctor]
        doctor_asignado = f"{nombres_doctor[doctor_idx]} {apellidos_doctor[doctor_idx]} (ID: {id_doctor[doctor_idx]})"
        nombres_turnos.append(nombre)
        numeros_socios.append(numero_socio)
        horarios.append(horario)
        tratamientos_turno.append((tratamiento, doctor_asignado))
        return f"Turno registrado. Doctor asignado: {doctor_asignado}"
    return "Opción de doctor inválida."



def mostrar_turnos(usuario, perfil):
    if perfil == "admin":
        print("1. Ver todos los turnos.")
        print("2. Ver los turnos de un tratamiento.")
        print("3. ver los turnos de un paciente especifico")
        try:
            opcion = int(input("Seleccione una opción: "))
        except ValueError:
            return "Opción inválida."

        if opcion == 1:
            if not nombres_turnos:
                return "No hay turnos registrados."
            turnos = list(zip(horarios, nombres_turnos, numeros_socios, tratamientos_turno))
            turnos.sort()
            for i, (horario, nombre, socio, (tratamiento, doctor)) in enumerate(turnos, 1):
                print(f"{i}. {nombre} - Socio: {socio} - Horario: {horario.strftime('%d/%m/%Y %H:%M')} - Tratamiento: {tratamiento} - Doctor: {doctor}")
            return "Turnos listados."

        elif opcion == 2:
            for i, t in enumerate(TRATAMIENTOS):
                print(f"{i+1}. {t}")
            try:
                idx = int(input("Seleccione tratamiento: ")) - 1
                if not (0 <= idx < len(TRATAMIENTOS)):
                    return "Tratamiento inválido."
                tratamiento_seleccionado = TRATAMIENTOS[idx]
            except ValueError:
                return "Entrada inválida. Debe ser un número."

            turnos = list(zip(horarios, nombres_turnos, numeros_socios, tratamientos_turno))
            turnos.sort()
            encontrados = False
            for i, (horario, nombre, socio, (tratamiento, doctor)) in enumerate(turnos, 1):
                if tratamiento == tratamiento_seleccionado:
                    print(f"{i}. {nombre} - Socio: {socio} - Horario: {horario.strftime('%d/%m/%Y %H:%M')} - Tratamiento: {tratamiento} - Doctor: {doctor}")
                    encontrados = True
            if not encontrados:
                return f"No hay turnos registrados para el tratamiento '{tratamiento_seleccionado}'."
            return "Turnos listados."
        elif opcion==3:
            resultado = mostrar_turno_paciente()
            print(resultado)
            
        else:
            return "Opción inválida."

    elif perfil == "medico":
        if not nombres_turnos:
            return "No hay turnos registrados."
        turnos = list(zip(horarios, nombres_turnos, numeros_socios, tratamientos_turno))
        turnos.sort()
        encontrados = False
        for i, (horario, nombre, socio, (tratamiento, doctor)) in enumerate(turnos, 1):
            if usuario.split("@")[0] in doctor:
                print(f"{i}. {nombre} - Socio: {socio} - Horario: {horario.strftime('%d/%m/%Y %H:%M')} - Tratamiento: {tratamiento} - Doctor: {doctor}")
                encontrados = True
        if not encontrados:
            return "No tiene turnos asignados."
        return "Turnos listados."

    elif perfil == "paciente":
        return mostrar_turno_paciente()
    return "Perfil desconocido."
        

def mostrar_turno_paciente():
    if not nombres_turnos:
        return "No hay turnos registrados."
    try:
        id_paciente = int(input("Ingrese el ID del paciente (número de socio): "))
    except ValueError:
        return "ID inválido. Debe ser un número."
    if id_paciente not in numeros_socios:
        return "ID no encontrado."
    turnos = list(zip(horarios, nombres_turnos, numeros_socios, tratamientos_turno))
    turnos.sort()
    encontrados = False
    for i, (horario, nombre, socio_id, (tratamiento, doctor)) in enumerate(turnos, 1):
        if socio_id == id_paciente:
            print(f"{i}. {nombre} - Socio: {socio_id} - Horario: {horario.strftime('%d/%m/%Y %H:%M')} - Tratamiento: {tratamiento} - Doctor: {doctor}")
            encontrados = True
    if not encontrados:
        return "El paciente no tiene turnos asignados."
    return "Turnos listados."

def eliminar_turno():
    mostrar_turnos(usuario_actual, perfil_actual)
    idx = int(input("Número de turno a eliminar: ")) - 1
    if 0 <= idx < len(nombres_turnos):
        nombres_turnos.pop(idx)
        numeros_socios.pop(idx)
        horarios.pop(idx)
        tratamientos_turno.pop(idx)
        return f"Se eliminó correctamente el turno de {nombres_turnos} (Nº socio {numeros_socios}) para la fecha {horarios.strftime('%d/%m/%Y %H:%M')}."
    return "Número de turno inválido."

def ver_agenda_diaria():
    if perfil_actual != "admin":
        return "Solo el perfil admin puede ver la agenda diaria."
    
    hoy = datetime.now().date()
    turnos_hoy = []
    for horario, nombre, socio_id, (tratamiento, doctor) in zip(horarios, nombres_turnos, numeros_socios, tratamientos_turno):
        if horario.date() == hoy:
            turnos_hoy.append((horario, nombre, socio_id, tratamiento, doctor))
    if not turnos_hoy:
        return "No hay turnos registrados para hoy."

    turnos_hoy.sort()
    print("\nAgenda del día de hoy:\n")
    for i, (horario, nombre, socio_id, tratamiento, doctor) in enumerate(turnos_hoy, 1):
        print(f"{i}. {nombre} - Socio: {socio_id} - {horario.strftime('%H:%M')} - Tratamiento: {tratamiento} - Doctor: {doctor}")
    return f"Total de turnos para hoy: {len(turnos_hoy)}"

def ver_agenda_diaria_medico():
    if perfil_actual != "medico":
        return "Solo el perfil médico puede ver su agenda diaria."

    if not nombres_turnos:
        return "No hay turnos registrados."
    id_ = input("Ingrese su ID de médico: ").strip()
    if id_ not in id_doctor:
        return "ID de médico no encontrado."
    hoy = datetime.now().date()
    turnos_hoy = []
    for horario, nombre, socio_id, (tratamiento, doctor) in zip(horarios, nombres_turnos, numeros_socios, tratamientos_turno):
        if horario.date() == hoy and id_ in doctor:
            turnos_hoy.append((horario, nombre, socio_id, tratamiento, doctor))
    if not turnos_hoy:
        return "No hay turnos registrados para hoy."
    
    turnos_hoy.sort()
    print(f"\nAgenda del día de hoy ({hoy.strftime('%d/%m/%Y')}) para el doctor con ID {id_}:\n")
    for i, (horario, nombre, socio_id, tratamiento, doctor) in enumerate(turnos_hoy, 1):
        print(f"{i}. {nombre} - Socio: {socio_id} - {horario.strftime('%H:%M')} - Tratamiento: {tratamiento} - Doctor: {doctor}")
    return f"Total de turnos para hoy: {len(turnos_hoy)}"


def mostrar_turno_doctor():
    if not nombres_turnos:
        return "No hay turnos registrados."
    id_ = input("ID del doctor cuyos turnos deseas ver: ")
    if id_ not in id_doctor:
        return "ID no encontrado."
    turnos = list(zip(horarios, nombres_turnos, numeros_socios, tratamientos_turno))
    turnos.sort()
    encontrados = False
    for i, (horario, nombre, socio, (tratamiento, doctor)) in enumerate(turnos, 1):
        if id_ in doctor:
            print(f"{i}. {nombre} - Socio: {socio} - Horario: {horario.strftime('%d/%m/%Y %H:%M')} - Tratamiento: {tratamiento} - Doctor: {doctor}")
            encontrados = True
    if not encontrados:
        return "El doctor no tiene turnos asignados." 
    return "Turnos listados."

def agregar_doctor():
    id_ = input("ID del doctor: ").strip()
    if id_ in id_doctor:
        return "El ID del doctor ya existe."
    nombre = input("Nombre: ")
    apellido = input("Apellido: ")
    for i, t in enumerate(TRATAMIENTOS):
        print(f"{i+1}. {t}")
    idx = int(input("Seleccione tratamiento: ")) - 1
    id_doctor.append(id_)
    nombres_doctor.append(nombre)
    apellidos_doctor.append(apellido)
    tratamientos_doctor.append(idx)
    return f"Doctor {nombre} {apellido} agregado."

def eliminar_doctor():
    if not id_doctor:
        return "No hay doctores registrados."
    
    id_ = input("ID del doctor a eliminar: ").strip()
    if id_ not in id_doctor:
        return "No se encontró el ID del doctor."

    idx = id_doctor.index(id_)
    tratamiento_doctor_elim = tratamientos_doctor[idx]
    otros_doctores_indices = [
        i for i, trat in enumerate(tratamientos_doctor)
        if trat == tratamiento_doctor_elim and id_doctor[i] != id_
    ]
    turnos_asignados = [
        i for i, (_, doctor_str) in enumerate(tratamientos_turno)
        if f"(ID: {id_})" in doctor_str
    ]
    mensaje = ""
    if turnos_asignados:
        if otros_doctores_indices:
            nuevo_doc_idx = otros_doctores_indices[0]
            nuevo_doc_nombre = f"{nombres_doctor[nuevo_doc_idx]} {apellidos_doctor[nuevo_doc_idx]} (ID: {id_doctor[nuevo_doc_idx]})"
            for t_idx in turnos_asignados:
                tratamiento_actual = tratamientos_turno[t_idx][0]
                tratamientos_turno[t_idx] = (tratamiento_actual, nuevo_doc_nombre)
            mensaje += f"Se reasignaron {len(turnos_asignados)} turno(s) al doctor {nuevo_doc_nombre}.\n"
        else:
            for t_idx in sorted(turnos_asignados, reverse=True):
                nombres_turnos.pop(t_idx)
                numeros_socios.pop(t_idx)
                horarios.pop(t_idx)
                tratamientos_turno.pop(t_idx)
            mensaje += f"No hay otro doctor en el tratamiento. Se eliminaron {len(turnos_asignados)} turno(s).\n"
    else:
        mensaje += "El doctor no tenía turnos asignados.\n"

    nombre = nombres_doctor.pop(idx)
    apellido = apellidos_doctor.pop(idx)
    id_doctor.pop(idx)
    tratamientos_doctor.pop(idx)

    mensaje += f"Doctor {nombre} {apellido} eliminado."
    return mensaje

def mostrar_doctores():
    for i in range(len(id_doctor)):
        t = TRATAMIENTOS[tratamientos_doctor[i]]
        print(f"{i+1}. {nombres_doctor[i]} {apellidos_doctor[i]} - ID: {id_doctor[i]} - Tratamiento: {t}")
    
    opcion = input("\n¿Desea ver los turnos de algún doctor? (s/n): ").lower()
    if opcion == "s":
        resultado = mostrar_turno_doctor()
        print(resultado)
    return "Fin de la lista."

def ingresar_tratamiento():
    print("Seleccione un tratamiento: ")
    for i, tratamiento in enumerate(TRATAMIENTOS, 1):
        print(f"\t{i}. {tratamiento}")
    while True:
        try:
            opcion = int(input(f"Ingrese opción 1 a {len(TRATAMIENTOS)}: "))
            if 1 <= opcion <= len(TRATAMIENTOS):
                return TRATAMIENTOS[opcion - 1]
            else:
                print("Opción no válida.")
        except ValueError:
            print("Debe ingresar un número válido.")

def ingresar_horario():
    while True:
        entrada = input("Fecha y hora (dd/mm/aaaa HH:MM): ")
        try:
            horario = datetime.strptime(entrada, "%d/%m/%Y %H:%M")
            if horario.weekday() == 6:  # Domingo
                print("No se atiende los domingos.")
                continue
            if horario.hour < APERTURA or horario.hour >= CIERRE:
                print(f"Los turnos deben ser entre las {APERTURA}:00 y las {CIERRE}:00.")
                continue
            if horario in horarios:
                print("Ese horario ya está ocupado.")
                continue
            return horario
        except ValueError:
            print("Formato inválido. Intente nuevamente.")


def imprimir_recibo(usuario, perfil):
    print("\n=== Generar recibo de turno ===")
    try:
        id = int(input("Ingrese el número de socio (paciente): ")) if perfil == "paciente" else input("Ingrese su ID de doctor: ").strip()
    except ValueError:
        return "ID inválido."

    encontrados = False
    recibos = []
    for horario, nombre_paciente, socio_id, (tratamiento, doctor_info) in zip(horarios, nombres_turnos, numeros_socios, tratamientos_turno):
        if (perfil == "paciente" and socio_id == id) or (perfil == "medico" and f"(ID: {id})" in doctor_info):
            if perfil == "paciente":
                recibo = f"Turno para: {nombre_paciente}\nFecha y hora: {horario.strftime('%d/%m/%Y %H:%M')}\nTratamiento: {tratamiento}\nMédico asignado: {doctor_info}\n"
            elif perfil == "medico":
                recibo = f"Paciente: {nombre_paciente} (Socio {socio_id})\nFecha y hora: {horario.strftime('%d/%m/%Y %H:%M')}\nTratamiento: {tratamiento}\n"
            print("\n--- RECIBO ---")
            print(recibo)
            recibos.append(recibo)
            encontrados = True

    if not encontrados:
        return "No se encontraron turnos asignados."

    filename = f"recibos_{perfil}_{id}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for r in recibos:
            f.write(r + "\n")
    return "Recibos generados correctamente."

usuario_actual, perfil_actual = menu_inicio()
if not usuario_actual:
    exit()
print("Acceso concedido al sistema del consultorio.")

cargar_datos()
while True:
    opcion = menu(perfil_actual)
    if opcion == 8:
        guardar_datos()
        print("\nPrograma finalizado por el usuario.")
        break
    if perfil_actual == "admin":
        acciones = [ingresar_turnos, lambda: mostrar_turnos(usuario_actual, perfil_actual),ver_agenda_diaria, eliminar_turno, agregar_doctor, eliminar_doctor, mostrar_doctores]
    elif perfil_actual == "paciente":
        acciones = [ingresar_turnos, lambda: mostrar_turnos(usuario_actual, perfil_actual), eliminar_turno, lambda: imprimir_recibo(usuario_actual, perfil_actual)]
    elif perfil_actual == "medico":
        acciones = [None, lambda: mostrar_turnos(usuario_actual, perfil_actual), ver_agenda_diaria_medico, lambda: imprimir_recibo(usuario_actual, perfil_actual)]
    try:
        funcion = acciones[opcion - 1]
        if funcion:
            resultado = funcion()
            print(resultado)
        else:
            print("Opción no permitida para este perfil.")
    except (IndexError, ValueError):
        print("Opción inválida.")
