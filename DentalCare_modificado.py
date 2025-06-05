
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os

ARCHIVO_JSON = "datos_consultorio.json"
TRATAMIENTOS = ['Control', 'Arreglo de caries', 'Ortodoncia', 'Extracción']
TURNOS_MAXIMOS = 23
APERTURA = 8
CIERRE = 20

datos_guardados = {
    "doctores": {"id": [], "nombres": [], "apellidos": [], "tratamientos": [], "Usuario": [], "Contraseña": []},
    "turnos": {"nombres": [], "apellidos": [], "numeros_socios": [], "horarios": [], "tratamientos": [], "doctor_asignado": []},
    "recepcion": {"nombres_recepcion": [], "Contraseña_recepcion": [], "doctor": [], "turnos": []},
    "paciente": {"Usuario_socio": [], "Contraseña_socio": [], "nombre": [], "turnos": []}
}

usuario_actual = None
perfil_actual = None

nombres_turnos = []
apellidos_turnos = []
numeros_socios = []
horarios = []
tratamientos_turno = []
doctores_asignados = []

id_doctor = []
nombres_doctor = []
apellidos_doctor = []
tratamientos_doctor = []

usuarios = {}

def cargar_datos():
    global usuarios
    if not os.path.exists(ARCHIVO_JSON):
        return
    with open(ARCHIVO_JSON, "r") as f:
        datos = json.load(f)
        datos_guardados.update(datos)

    id_doctor.extend(datos.get("doctores", {}).get("id", []))
    nombres_doctor.extend(datos.get("doctores", {}).get("nombres", []))
    apellidos_doctor.extend(datos.get("doctores", {}).get("apellidos", []))
    tratamientos_doctor.extend(datos.get("doctores", {}).get("tratamientos", []))

    nombres_turnos.extend(datos.get("turnos", {}).get("nombres", []))
    apellidos_turnos.extend(datos.get("turnos", {}).get("apellidos", []))
    numeros_socios.extend(datos.get("turnos", {}).get("numeros_socios", []))
    horarios.extend(datos.get("turnos", {}).get("horarios", []))
    tratamientos_turno.extend(datos.get("turnos", {}).get("tratamientos", []))
    doctores_asignados.extend(datos.get("turnos", {}).get("doctor_asignado", []))

    for i, user in enumerate(datos.get("paciente", {}).get("Usuario_socio", [])):
        usuarios[user] = {"clave": datos["paciente"]["Contraseña_socio"][i], "perfil": "paciente"}
    for i, user in enumerate(datos.get("recepcion", {}).get("nombres_recepcion", [])):
        usuarios[user] = {"clave": datos["recepcion"]["Contraseña_recepcion"][i], "perfil": "admin"}
    for i, user in enumerate(datos.get("doctores", {}).get("Usuario", [])):
        usuarios[user] = {"clave": datos["doctores"]["Contraseña"][i], "perfil": "medico"}

def guardar_datos():
    datos = {
        "doctores": {
            "id": id_doctor,
            "nombres": nombres_doctor,
            "apellidos": apellidos_doctor,
            "tratamientos": tratamientos_doctor,
            "Usuario": [k for k,v in usuarios.items() if v["perfil"] == "medico"],
            "Contraseña": [v["clave"] for k,v in usuarios.items() if v["perfil"] == "medico"]
        },
        "turnos": {
            "nombres": nombres_turnos,
            "apellidos": apellidos_turnos,
            "numeros_socios": numeros_socios,
            "horarios": horarios,
            "tratamientos": tratamientos_turno,
            "doctor_asignado": doctores_asignados
        },
        "recepcion": {
            "nombres_recepcion": [k for k,v in usuarios.items() if v["perfil"] == "admin"],
            "Contraseña_recepcion": [v["clave"] for k,v in usuarios.items() if v["perfil"] == "admin"],
            "doctor": [], "turnos": []
        },
        "paciente": {
            "Usuario_socio": [k for k,v in usuarios.items() if v["perfil"] == "paciente"],
            "Contraseña_socio": [v["clave"] for k,v in usuarios.items() if v["perfil"] == "paciente"],
            "nombre": [], "turnos": []
        }
    }
    with open(ARCHIVO_JSON, "w") as f:
        json.dump(datos, f, indent=4)

# === Aquí irán las funciones del sistema, login, interfaz y las nuevas integraciones ===

def buscar(item, arreglo):
    try:
        return arreglo.index(item)
    except ValueError:
        return -1

def validar_horario(horario):
    try:
        hora = float(horario)
        if APERTURA <= hora < CIERRE and hora not in horarios:
            minutos = int((hora - int(hora)) * 100)
            return minutos in [0, 30]
    except Exception:
        return False
    return False

def ingresar_turno():
    if perfil_actual == "medico":
        messagebox.showinfo("Restringido", "Los médicos no pueden ingresar turnos.")
        return

    if len(nombres_turnos) >= TURNOS_MAXIMOS:
        messagebox.showerror("Turnos llenos", "No hay turnos disponibles.")
        return

    try:
        socio = int(simpledialog.askstring("Turno", "Ingrese número de socio:"))
        if perfil_actual == "paciente" and usuario_actual != str(socio):
            messagebox.showwarning("Acceso denegado", "Solo puedes agendar tu propio turno.")
            return

        if buscar(socio, numeros_socios) != -1:
            messagebox.showwarning("Turno existente", "El socio ya tiene un turno.")
            return

        nombre = simpledialog.askstring("Turno", "Nombre del paciente:")
        apellido = simpledialog.askstring("Turno", "Apellido del paciente:")
        horario = simpledialog.askstring("Turno", "Horario (Ej: 9.30):")
        if not validar_horario(horario):
            messagebox.showerror("Horario inválido", "Debe ser entre 8 y 20 hs, con minutos :00 o :30, y no ocupado.")
            return

        tratamiento = simpledialog.askinteger("Tratamiento", f"Seleccione:\n" + "\n".join(f"{i+1}. {t}" for i, t in enumerate(TRATAMIENTOS)))
        if not (1 <= tratamiento <= len(TRATAMIENTOS)):
            raise ValueError()

        nombres_turnos.append(nombre)
        apellidos_turnos.append(apellido)
        numeros_socios.append(socio)
        horarios.append(float(horario))
        tratamientos_turno.append(TRATAMIENTOS[tratamiento - 1])
        doctores_asignados.append("")
        guardar_datos()
        messagebox.showinfo("Éxito", "Turno guardado correctamente.")
    except Exception:
        messagebox.showerror("Error", "Entrada inválida.")


def ver_turnos():
    if perfil_actual == "medico":
        mensaje = "Turnos asignados al médico:\n"
        for i in range(len(doctores_asignados)):
            if usuario_actual in doctores_asignados[i]:
                mensaje += f"{i+1}. {apellidos_turnos[i]} {nombres_turnos[i]} - Socio: {numeros_socios[i]} - Hora: {horarios[i]} - Tratamiento: {tratamientos_turno[i]}\n"
    elif perfil_actual == "paciente":
        mensaje = "Tus turnos:\n"
        for i in range(len(numeros_socios)):
            if str(numeros_socios[i]) == usuario_actual:
                mensaje += f"{i+1}. {apellidos_turnos[i]} {nombres_turnos[i]} - Hora: {horarios[i]} - Tratamiento: {tratamientos_turno[i]}\n"
    else:
        mensaje = "Todos los turnos:\n"
        for i in range(len(nombres_turnos)):
            mensaje += f"{i+1}. {apellidos_turnos[i]} {nombres_turnos[i]} - Socio: {numeros_socios[i]} - Hora: {horarios[i]} - Tratamiento: {tratamientos_turno[i]}\n"

    messagebox.showinfo("Turnos", mensaje if mensaje.strip() else "No hay turnos.")

def eliminar_turno():
    try:
        socio = int(simpledialog.askstring("Eliminar turno", "Número de socio:"))
        i = buscar(socio, numeros_socios)
        if i == -1 or (perfil_actual == "paciente" and str(socio) != usuario_actual):
            messagebox.showinfo("No permitido", "Turno no encontrado o no autorizado.")
            return
        nombres_turnos.pop(i)
        apellidos_turnos.pop(i)
        numeros_socios.pop(i)
        horarios.pop(i)
        tratamientos_turno.pop(i)
        doctores_asignados.pop(i)
        guardar_datos()
        messagebox.showinfo("Eliminado", "Turno eliminado.")
    except Exception:
        messagebox.showerror("Error", "Entrada inválida.")

def agregar_doctor():
    if perfil_actual != "admin":
        messagebox.showwarning("Acceso denegado", "Solo un administrador puede agregar doctores.")
        return

    nombre = simpledialog.askstring("Agregar doctor", "Nombre:")
    apellido = simpledialog.askstring("Agregar doctor", "Apellido:")
    clave = simpledialog.askstring("Contraseña del doctor", "Contraseña:")
    tratamiento = simpledialog.askinteger("Tratamiento", f"Seleccione:\n" + "\n".join(f"{i+1}. {t}" for i, t in enumerate(TRATAMIENTOS)))

    if not nombre or not apellido or not clave or not tratamiento:
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return

    usuario = f"{apellido.lower()}{nombre[0].lower()}@dentalcare.com"
    if usuario in usuarios:
        messagebox.showerror("Duplicado", f"El usuario {usuario} ya existe.")
        return

    nuevo_id = 1
    while nuevo_id in id_doctor:
        nuevo_id += 1

    id_doctor.append(nuevo_id)
    nombres_doctor.append(nombre)
    apellidos_doctor.append(apellido)
    tratamientos_doctor.append(TRATAMIENTOS[tratamiento - 1])
    usuarios[usuario] = {"clave": clave, "perfil": "medico"}

    guardar_datos()
    messagebox.showinfo("Agregado", f"Doctor registrado correctamente con el usuario:\n{usuario}")
