import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os

# === Estilo Moderno ===
def configurar_estilo_ventana(ventana):
    ventana.configure(bg="#f0f4f8")
    ventana.option_add("*Font", "Segoe UI 10")
    ventana.option_add("*Button.Background", "#007acc")
    ventana.option_add("*Button.Foreground", "white")
    ventana.option_add("*Button.Relief", "flat")
    ventana.option_add("*Label.Background", "#f0f4f8")
    ventana.option_add("*Label.Foreground", "#333333")

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
    if not os.path.exists(USUARIOS_JASON):
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
    with open(USUARIOS_JASON, "w") as f:
        json.dump(datos, f, indent=4)

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
    mensaje = ""
    for i in range(len(id_doctor)):
        nombre = nombres_doctor[i]
        apellido = apellidos_doctor[i]
        email_generado = f"{apellido.lower()}{nombre[0].lower()}@dentalcare.com"
        mensaje += (
            f"ID:{id_doctor[i]} - Dr. {apellido} {nombre} - "
            f"{tratamientos_doctor[i]} - Usuario: {email_generado}\n"
        )
    messagebox.showinfo("Doctores", mensaje if mensaje else "No hay doctores registrados.")

def buscar_turnos_filtrados():
    if perfil_actual != "admin":
        return
    opcion = simpledialog.askinteger("Buscar", "1. Por paciente (nro socio)\n2. Por tratamiento")
    if opcion == 1:
        try:
            socio = int(simpledialog.askstring("Paciente", "Número de socio:"))
            mensaje = ""
            for i in range(len(numeros_socios)):
                if numeros_socios[i] == socio:
                    mensaje += f"{i+1}. {apellidos_turnos[i]} {nombres_turnos[i]} - Hora: {horarios[i]} - Tratamiento: {tratamientos_turno[i]}\n"
            messagebox.showinfo("Turnos del paciente", mensaje or "No se encontraron turnos.")
        except Exception:
            messagebox.showerror("Error", "Entrada inválida.")
    elif opcion == 2:
        seleccion = simpledialog.askinteger("Tratamiento", "\n".join(f"{i+1}. {t}" for i, t in enumerate(TRATAMIENTOS)))
        if not seleccion or not (1 <= seleccion <= len(TRATAMIENTOS)):
            return
        tratamiento = TRATAMIENTOS[seleccion - 1]
        mensaje = ""
        for i in range(len(tratamientos_turno)):
            if tratamientos_turno[i] == tratamiento:
                mensaje += f"{i+1}. {apellidos_turnos[i]} {nombres_turnos[i]} - Socio: {numeros_socios[i]} - Hora: {horarios[i]}\n"
        messagebox.showinfo("Turnos por tratamiento", mensaje or "No se encontraron turnos.")

def salir():
    guardar_datos()
    if messagebox.askokcancel("Salir", "¿Desea salir del sistema?"):
        root.destroy()

def verificar_login():
    global usuario_actual, perfil_actual
    u = entry_usuario.get().strip()
    c = entry_clave.get().strip()

    if u in usuarios and usuarios[u]["clave"] == c:
        usuario_actual = u
        perfil_actual = usuarios[u]["perfil"]
    else:
        messagebox.showerror("Login incorrecto", "Usuario o contraseña incorrectos.")
        return

    login_win.destroy()
    iniciar_interfaz()

def registrar_usuario():
    def guardar_registro():
        nuevo_usuario = entry_nuevo_usuario.get().strip()
        nueva_clave = entry_nueva_clave.get().strip()

        if not nuevo_usuario or not nueva_clave:
            messagebox.showwarning("Datos incompletos", "Complete usuario y contraseña.")
            return

        if nuevo_usuario in usuarios:
            messagebox.showerror("Error", "El usuario ya existe.")
            return

        if "@dentalcare.com" in nuevo_usuario:
            perfil = "medico"
        elif "@gmail.com" in nuevo_usuario:
            perfil = "paciente"
        else:
            messagebox.showerror("Error", "Dominio no válido. Use @gmail.com o @dentalcare.com")
            return

        usuarios[nuevo_usuario] = {"clave": nueva_clave, "perfil": perfil}

        if perfil == "medico":
            if nuevo_usuario not in datos_guardados["doctores"]["Usuario"]:
                datos_guardados["doctores"]["Usuario"].append(nuevo_usuario)
                datos_guardados["doctores"]["Contraseña"].append(nueva_clave)
        elif perfil == "paciente":
            if nuevo_usuario not in datos_guardados["paciente"]["Usuario_socio"]:
                datos_guardados["paciente"]["Usuario_socio"].append(nuevo_usuario)
                datos_guardados["paciente"]["Contraseña_socio"].append(nueva_clave)

        guardar_datos()
        messagebox.showinfo("Registrado", f"Usuario {nuevo_usuario} registrado con éxito.")
        ventana_registro.destroy()

    ventana_registro = tk.Toplevel(login_win)
    ventana_registro.title("Registrar nuevo usuario")
    ventana_registro.geometry("300x180")

    tk.Label(ventana_registro, text="Nuevo usuario:").pack(pady=5)
    entry_nuevo_usuario = tk.Entry(ventana_registro)
    entry_nuevo_usuario.pack()

    tk.Label(ventana_registro, text="Nueva contraseña:").pack(pady=5)
    entry_nueva_clave = tk.Entry(ventana_registro, show="*")
    entry_nueva_clave.pack()

    tk.Button(ventana_registro, text="Registrar", command=guardar_registro).pack(pady=10)

def iniciar_interfaz():
    global root
    root = tk.Tk(); configurar_estilo_ventana(root); configurar_estilo_ventana(login_win)
    root.title("=== DentalCare ===")
    root.geometry("350x400")

    ttk.Label(root, text=f"Bienvenido, {usuario_actual} ({perfil_actual})").pack(pady=10)

    ttk.Button(root, text="Ingresar turno", command=ingresar_turno).pack(fill='x', padx=50, pady=5)
    ttk.Button(root, text="Ver turnos", command=ver_turnos).pack(fill='x', padx=50, pady=5)
    ttk.Button(root, text="Eliminar turno", command=eliminar_turno).pack(fill='x', padx=50, pady=5)

    if perfil_actual == "admin":
        ttk.Button(root, text="Agregar doctor", command=agregar_doctor).pack(fill='x', padx=50, pady=5)
        ttk.Button(root, text="Eliminar doctor", command=eliminar_doctor).pack(fill='x', padx=50, pady=5)
        ttk.Button(root, text="Buscar turnos por paciente/tratamiento", command=buscar_turnos_filtrados).pack(fill='x', padx=50, pady=5)

    ttk.Button(root, text="Mostrar doctores", command=mostrar_doctores).pack(fill='x', padx=50, pady=5)
    ttk.Button(root, text="Salir", command=salir).pack(fill='x', padx=50, pady=20)

    root.mainloop()

# Inicio
cargar_datos()
login_win = tk.Tk()
login_win.title("=== Consultorio Odontológico ===")
login_win.geometry("300x220")

tk.Label(login_win, text="Usuario:").pack(pady=5)
entry_usuario = tk.Entry(login_win)
entry_usuario.pack()

tk.Label(login_win, text="Contraseña:").pack(pady=5)
entry_clave = tk.Entry(login_win, show="*")
entry_clave.pack()

tk.Button(login_win, text="Ingresar", command=verificar_login).pack(pady=10)
tk.Button(login_win, text="Registrarse", command=registrar_usuario).pack()

login_win.mainloop()

