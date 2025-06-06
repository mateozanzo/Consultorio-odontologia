
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
USUARIOS_JASON = "usuarios.json"
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
    print("Cargando datos desde:", os.path.abspath(USUARIOS_JASON))
    if not os.path.exists(USUARIOS_JASON):
        print("Archivo usuarios.json no encontrado.")
        return
    with open(USUARIOS_JASON, "r") as f:
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

    recepcion = datos.get("recepcion", {})
    nombres = recepcion.get("nombres_recepcion", [])
    claves = recepcion.get("Contraseña_recepcion", recepcion.get("contraseña_recepcion", []))
    for i, user in enumerate(nombres):
        usuarios[user] = {"clave": claves[i], "perfil": "admin"}

    for i, user in enumerate(datos.get("doctores", {}).get("Usuario", [])):
        usuarios[user] = {"clave": datos["doctores"]["Contraseña"][i], "perfil": "medico"}

    print("Usuarios cargados:", usuarios)

# Mostrar los usuarios cargados antes del login
cargar_datos()

# Login
login_win = tk.Tk()
login_win.title("=== Consultorio Odontológico ===")
login_win.geometry("300x220")

tk.Label(login_win, text="Usuario:").pack(pady=5)
entry_usuario = tk.Entry(login_win)
entry_usuario.pack()

tk.Label(login_win, text="Contraseña:").pack(pady=5)
entry_clave = tk.Entry(login_win, show="*")
entry_clave.pack()

def verificar_login():
    global usuario_actual, perfil_actual
    u = entry_usuario.get().strip()
    c = entry_clave.get().strip()

    print(f"Intentando login con usuario: {u}, contraseña: {c}")
    if u in usuarios and usuarios[u]["clave"] == c:
        usuario_actual = u
        perfil_actual = usuarios[u]["perfil"]
        print("Login exitoso.")
    else:
        print("Login fallido.")
        messagebox.showerror("Login incorrecto", "Usuario o contraseña incorrectos.")
        return

    login_win.destroy()
    tk.messagebox.showinfo("Éxito", f"Iniciaste sesión como {usuario_actual} ({perfil_actual})")

tk.Button(login_win, text="Ingresar", command=verificar_login).pack(pady=10)

login_win.mainloop()
