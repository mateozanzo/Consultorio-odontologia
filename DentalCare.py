import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import datetime

USUARIOS_JSON = "usuarios.json"
TRATAMIENTOS = ['Control', 'Arreglo de caries', 'Ortodoncia', 'Extracción']
TURNOS_MAXIMOS = 23
APERTURA = 8
CIERRE = 20

# Variables globales
datos_guardados = {
    "doctores": {"id": [], "nombres": [], "apellidos": [], "tratamientos": [], "Usuario": [], "Contraseña": []},
    "turnos": {"nombres": [], "apellidos": [], "numeros_socios": [], "horarios": [], "tratamientos": [], "doctor_asignado": []},
    "recepcion": {"nombres_recepcion": [], "Contraseña_recepcion": [], "doctor": [], "turnos": []},
    "paciente": {"Usuario_socio": [], "Contraseña_socio": [], "nombre": [], "turnos": [], "ids_socio": []}
}

usuario_actual = None
perfil_actual = None

# Listas para el sistema
nombres_turnos = []
apellidos_turnos = []
numeros_socios = []
horarios = []
tratamientos_turno = []
doctores_asignados = []
ids_turnos = []


id_doctor = []
nombres_doctor = []
apellidos_doctor = []
tratamientos_doctor = []

usuarios = {}

# Cargar datos desde JSON
def cargar_datos():
    global usuarios
    usuarios["dentalCare"] = {"clave": "123456", "perfil": "admin"}

    if not os.path.exists(USUARIOS_JSON):
        return

    with open(USUARIOS_JSON, "r") as f:
        datos = json.load(f)

    datos.setdefault("paciente", {"Usuario_socio": [], "Contraseña_socio": [], "nombre": [], "turnos": [], "ids_socio": []})
    datos.setdefault("recepcion", {"nombres_recepcion": [], "Contraseña_recepcion": [], "doctor": [], "turnos": []})

    datos_guardados.update(datos)

    id_doctor.clear()
    id_doctor.extend(datos.get("doctores", {}).get("id", []))
    nombres_doctor.clear()
    nombres_doctor.extend(datos.get("doctores", {}).get("nombres", []))
    apellidos_doctor.clear()
    apellidos_doctor.extend(datos.get("doctores", {}).get("apellidos", []))
    tratamientos_doctor.clear()
    tratamientos_doctor.extend(datos.get("doctores", {}).get("tratamientos", []))

    nombres_turnos.clear()
    nombres_turnos.extend(datos.get("turnos", {}).get("nombres", []))
    apellidos_turnos.clear()
    apellidos_turnos.extend(datos.get("turnos", {}).get("apellidos", []))
    numeros_socios.clear()
    numeros_socios.extend(datos.get("turnos", {}).get("numeros_socios", []))
    horarios.clear()
    horarios.extend([datetime.datetime.strptime(h, "%Y-%m-%d %H:%M") for h in datos.get("turnos", {}).get("horarios", [])])
    tratamientos_turno.clear()
    tratamientos_turno.extend(datos.get("turnos", {}).get("tratamientos", []))
    doctores_asignados.clear()
    doctores_asignados.extend(datos.get("turnos", {}).get("doctor_asignado", []))
    ids = datos.get("turnos", {}).get("ids")
    if ids is None or len(ids) != len(datos.get("turnos", {}).get("nombres", [])):
        ids = list(range(1, len(datos.get("turnos", {}).get("nombres", [])) + 1))
    ids_turnos.clear()
    ids_turnos.extend(ids)

    usuarios.clear()
    usuarios["dentalCare"] = {"clave": "123456", "perfil": "admin"}

    for i, user in enumerate(datos["paciente"]["Usuario_socio"]):
        clave = datos["paciente"]["Contraseña_socio"][i] if i < len(datos["paciente"]["Contraseña_socio"]) else ""
        usuario_id = datos["paciente"]["ids_socio"][i] if i < len(datos["paciente"]["ids_socio"]) else None
        usuarios[user] = {"clave": clave, "perfil": "paciente", "id": usuario_id}

    for i, user in enumerate(datos["recepcion"]["nombres_recepcion"]):
        clave = datos["recepcion"]["Contraseña_recepcion"][i] if i < len(datos["recepcion"]["Contraseña_recepcion"]) else ""
        usuarios[user] = {"clave": clave, "perfil": "admin"}

    for i, user in enumerate(datos.get("doctores", {}).get("Usuario", [])):
        clave = datos.get("doctores", {}).get("Contraseña", [])[i] if i < len(datos.get("doctores", {}).get("Contraseña", [])) else ""
        usuarios[user] = {"clave": clave, "perfil": "medico"}

# Guardar datos en JSON
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
            "horarios": [h.strftime("%Y-%m-%d %H:%M") for h in horarios],
            "tratamientos": tratamientos_turno,
            "doctor_asignado": doctores_asignados
        },
        "recepcion": {
            "nombres_recepcion": [k for k,v in usuarios.items() if v["perfil"] == "admin" and k != "dentalCare"],
            "Contraseña_recepcion": [v["clave"] for k,v in usuarios.items() if v["perfil"] == "admin" and k != "dentalCare"],
            "doctor": [], "turnos": []
        },
        "paciente": {
            "Usuario_socio": [k for k,v in usuarios.items() if v["perfil"] == "paciente"],
            "Contraseña_socio": [v["clave"] for k,v in usuarios.items() if v["perfil"] == "paciente"],
            "nombre": [], "turnos": [],
            "ids_socio": [usuarios[k]["id"] for k,v in usuarios.items() if v["perfil"] == "paciente"]
        }
    }
    with open(USUARIOS_JSON, "w") as f:
        json.dump(datos, f, indent=4)

def buscar(item, arreglo):
    try:
        return arreglo.index(item)
    except ValueError:
        return -1



def ingresar_turno():
    global perfil_actual, usuario_actual

    if perfil_actual == "medico":
        messagebox.showinfo("Restringido", "Los médicos no pueden ingresar turnos.")
        return

    if len(nombres_turnos) >= TURNOS_MAXIMOS:
        messagebox.showerror("Turnos llenos", "No hay turnos disponibles.")
        return

    try:
        if perfil_actual == "paciente":
            socio = usuarios[usuario_actual].get("id")
        else:
            socio_str = simpledialog.askstring("Turno", "Ingrese número de socio:")
            if socio_str is None:
                return
            socio = int(socio_str)

        lista_ids = datos_guardados["paciente"].get("ids_socio", [])
        if socio not in lista_ids:
            messagebox.showerror("No válido", f"El número de socio {socio} no está registrado.")
            return

        nombre = simpledialog.askstring("Turno", "Nombre del paciente:")
        apellido = simpledialog.askstring("Turno", "Apellido del paciente:")

        fecha_str = simpledialog.askstring("Turno", "Fecha del turno (DD-MM-AAAA):")
        if fecha_str is None:
            return
        try:
            dia, mes, anio = map(int, fecha_str.split('-'))
            fecha_turno = datetime.date(anio, mes, dia)
        except ValueError:
            messagebox.showerror("Fecha inválida", "Formato de fecha incorrecto. Use DD-MM-AAAA.")
            return
        horario_str = simpledialog.askstring("Turno", "Horario (Ej: 9:00 o 9:30):") 
        if not (nombre and apellido and horario_str):
                    return
        try:
            hora_int, minutos_int = map(int, horario_str.split(':'))
            if minutos_int not in [0, 30]:
                raise ValueError("Los minutos deben ser :00 o :30")
            turno_datetime = datetime.datetime(fecha_turno.year, fecha_turno.month, fecha_turno.day, hora_int, minutos_int)
            # valida que no sea una fecha pasada
            if turno_datetime < datetime.datetime.now():
                messagebox.showerror("Horario inválido", "No puedes seleccionar una fecha y hora pasadas.")
                return
            
            # Validar que el horario esté dentro del rango de apertura y cierre
            if not (APERTURA <= turno_datetime.hour < CIERRE):
                messagebox.showerror("Horario inválido", f"El horario debe ser entre las {APERTURA}:00 y las {CIERRE}:00.")
                return
            if turno_datetime in horarios:
                messagebox.showerror("Horario ocupado", "Ese horario ya está ocupado para esa fecha.")
                return
        except ValueError as e:
            messagebox.showerror("Horario inválido", f"Formato de horario incorrecto o minutos inválidos. {e}")
            return

        tratamiento = simpledialog.askinteger("Tratamiento", f"Seleccione:\n" + "\n".join(f"{i+1}. {t}" for i, t in enumerate(TRATAMIENTOS)))
        if not tratamiento or not (1 <= tratamiento <= len(TRATAMIENTOS)):
            raise ValueError()
        nuevo_id = 1
        while nuevo_id in ids_turnos:
            nuevo_id += 1
        ids_turnos.append(nuevo_id)

        nombres_turnos.append(nombre)
        apellidos_turnos.append(apellido)
        numeros_socios.append(socio)
        horarios.append(turno_datetime)
        tratamientos_turno.append(TRATAMIENTOS[tratamiento - 1])

        # Asignar doctor al final del proceso
        doctor_asignado = ""
        
        if len(id_doctor) == 0:
            messagebox.showerror("Sin doctores", "No hay doctores disponibles para asignar.")
            return

        opciones_doc = [
            f"{id_doctor[i]} - Dr. {apellidos_doctor[i]} {nombres_doctor[i]}"
            for i in range(len(id_doctor))
            if tratamientos_doctor[i] == TRATAMIENTOS[tratamiento - 1]
        ]

        if not opciones_doc:
            messagebox.showerror("Sin coincidencias", "No hay doctores disponibles para el tratamiento seleccionado.")
            return

        opcion = simpledialog.askstring(
            "Seleccionar Doctor",
            "Seleccione el doctor deseado por ID:\n" + "\n".join(opciones_doc)
        )
        if opcion is None:
            return
        try:
            id_sel = int(opcion.split()[0])
            idx_doc = id_doctor.index(id_sel)
            doctor_asignado = f"{nombres_doctor[idx_doc]} {apellidos_doctor[idx_doc]} ( ID: {id_doctor[idx_doc]})"
        except Exception:
            messagebox.showerror("Error", "ID de doctor inválido.")
            return
        
        doctores_asignados.append(doctor_asignado)

        guardar_datos()
        messagebox.showinfo("Éxito", "Turno guardado correctamente " f"ids: {nuevo_id}")
    except Exception as e:
        messagebox.showerror("Error", f"Entrada inválida: {e}")


def ver_turnos():
    global perfil_actual, usuario_actual
    
    mensaje = ""
    turnos_filtrados = []
    if perfil_actual == "medico":
        # Identificar al médico actual
        nombre_completo_medico = None
        for i in range(len(id_doctor)):
            expected_user = f"{apellidos_doctor[i].lower()}{nombres_doctor[i][0].lower()}@dentalcare.com"
            if expected_user == usuario_actual:
                nombre_completo_medico = f"{nombres_doctor[i]} {apellidos_doctor[i]} ( ID: {id_doctor[i]})"
                break
        if not nombre_completo_medico:
            messagebox.showerror("Error", "No se pudo identificar al médico actual.")
            return
        
        mensaje = "Turnos asignados a usted:\n"
        for i in range(len(doctores_asignados)):
            if doctores_asignados[i] == nombre_completo_medico:
                turnos_filtrados.append({
                    "id": ids_turnos[i],
                    "nombre": nombres_turnos[i],
                    "apellido": apellidos_turnos[i],
                    "socio": numeros_socios[i],
                    "horario": horarios[i], 
                    "tratamiento": tratamientos_turno[i]
                })

    elif perfil_actual == "paciente":
        mensaje = "Tus turnos:\n"
        socio_paciente = usuarios[usuario_actual].get("id")
        for i in range(len(numeros_socios)):
            if numeros_socios[i] == socio_paciente:
                turnos_filtrados.append({
                    "id": ids_turnos[i],
                    "nombre": nombres_turnos[i],
                    "apellido": apellidos_turnos[i],
                    "socio": numeros_socios[i],
                    "horario": horarios[i], 
                    "tratamiento": tratamientos_turno[i],
                    "doctor_asignado": doctores_asignados[i]
                })
    else: # Admin o Recepción
        mensaje = "Todos los turnos:\n"
        for i in range(len(nombres_turnos)):
            turnos_filtrados.append({
                "id": ids_turnos[i],
                "nombre": nombres_turnos[i],
                "apellido": apellidos_turnos[i],
                "socio": numeros_socios[i],
                "horario": horarios[i], 
                "tratamiento": tratamientos_turno[i],
                "doctor_asignado": doctores_asignados[i]
            })
    
    if not turnos_filtrados:
        mensaje += "No hay turnos."
    else:
        # Ordenar turnos por fecha y hora
        turnos_filtrados.sort(key=lambda x: x["horario"])
        for turno in turnos_filtrados:
            fecha_hora_str = turno["horario"].strftime("%d-%m-%Y %H:%M")
            linea = f"ID {turno['id']} - {turno['apellido']} {turno['nombre']} - "
            if perfil_actual != "paciente": # Mostrar socio solo si no es paciente viendo sus propios turnos
                linea += f"Socio: {turno['socio']} - "
            linea += f"Fecha y Hora: {fecha_hora_str} - Tratamiento: {turno['tratamiento']}"
            if perfil_actual != "medico": # Mostrar doctor asignado solo si no es médico viendo sus propios turnos
                linea += f" - Doctor: {turno.get('doctor_asignado', 'N/A')}"
            mensaje += linea + "\n"
    messagebox.showinfo("Turnos", mensaje)


def eliminar_turno():
    global perfil_actual, usuario_actual
    try:
        id_str = simpledialog.askstring("Eliminar turno", "Ingrese ID del turno a eliminar:")
        if id_str is None:
            return
        id_turno = int(id_str)

        if id_turno not in ids_turnos:
            messagebox.showerror("Error", "ID de turno no encontrado.")
            return

        i = ids_turnos.index(id_turno)

        # Verificación según perfil
        if perfil_actual == "paciente":
            socio_paciente = usuarios[usuario_actual].get("id")
            if numeros_socios[i] != socio_paciente:
                messagebox.showerror("Acceso denegado", "Ese turno no te pertenece.")
                return
        elif perfil_actual == "medico":
            nombre_mi_doc = None
            for idx in range(len(id_doctor)):
                email_doc = f"{apellidos_doctor[idx].lower()}{nombres_doctor[idx][0].lower()}@dentalcare.com"
                if email_doc == usuario_actual:
                    nombre_mi_doc = f"{nombres_doctor[idx]} {apellidos_doctor[idx]} (ID: {id_doctor[idx]})"
                    break
            if doctores_asignados[i] != nombre_mi_doc:
                messagebox.showerror("Acceso denegado", "Ese turno no está asignado a usted.")
                return

        if not messagebox.askyesno("Confirmar", "¿Seguro que desea eliminar este turno?"):
            return

        # Eliminar turno de todas las listas
        ids_turnos.pop(i)
        nombres_turnos.pop(i)
        apellidos_turnos.pop(i)
        numeros_socios.pop(i)
        horarios.pop(i)
        tratamientos_turno.pop(i)
        doctores_asignados.pop(i)

        guardar_datos()
        messagebox.showinfo("Eliminado", "Turno eliminado con éxito.")
    except Exception:
        messagebox.showerror("Error", "Entrada inválida.")


def agregar_doctor():
    global perfil_actual
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

    if not (1 <= tratamiento <= len(TRATAMIENTOS)):
        messagebox.showerror("Error", "Tratamiento inválido.")
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
    global perfil_actual
    if perfil_actual != "admin":
        messagebox.showwarning("Acceso denegado", "Solo un administrador puede eliminar doctores.")
        return

    if not id_doctor:
        messagebox.showinfo("Sin doctores", "No hay doctores registrados.")
        return

    try:
        id_eliminar = simpledialog.askinteger("Eliminar doctor", "ID del doctor a eliminar:")
        if id_eliminar is None:
            return
        if id_eliminar not in id_doctor:
            messagebox.showerror("Error", "No se encontró el ID del doctor.")
            return

        idx = id_doctor.index(id_eliminar)
        tratamiento_elim = tratamientos_doctor[idx]
        otros_doctores = [
            i for i, trat in enumerate(tratamientos_doctor)
            if trat == tratamiento_elim and id_doctor[i] != id_eliminar
        ]

        turnos_asignados = [
            i for i, doc in enumerate(doctores_asignados)
            if doc and str(id_eliminar) in doc
        ]

        mensaje = ""
        if turnos_asignados:
            if otros_doctores:
                nuevo_idx = otros_doctores[0]
                nuevo_doc = f"{nombres_doctor[nuevo_idx]} {apellidos_doctor[nuevo_idx]} (ID: {id_doctor[nuevo_idx]})"
                for t in turnos_asignados:
                    doctores_asignados[t] = nuevo_doc
                mensaje += f"Se reasignaron {len(turnos_asignados)} turno(s) al doctor {nuevo_doc}.\n"
            else:
                for t in sorted(turnos_asignados, reverse=True):
                    nombres_turnos.pop(t)
                    apellidos_turnos.pop(t)
                    numeros_socios.pop(t)
                    horarios.pop(t)
                    tratamientos_turno.pop(t)
                    doctores_asignados.pop(t)
                mensaje += f"No hay otro doctor en el tratamiento. Se eliminaron {len(turnos_asignados)} turno(s).\n"
        else:
            mensaje += "El doctor no tenía turnos asignados.\n"

        nombre = nombres_doctor.pop(idx)
        apellido = apellidos_doctor.pop(idx)
        id_doctor.pop(idx)
        tratamientos_doctor.pop(idx)

        email = f"{apellido.lower()}{nombre[0].lower()}@dentalcare.com"
        usuarios.pop(email, None)

        guardar_datos()
        messagebox.showinfo("Doctor eliminado", mensaje + f"Doctor {nombre} {apellido} eliminado.")
    except Exception:
        messagebox.showerror("Error", "Entrada inválida.")

def mostrar_doctores():
    mensaje = ""
    for i in range(len(id_doctor)):
        nombre = nombres_doctor[i]
        apellido = apellidos_doctor[i]
        email = f"{apellido.lower()}{nombre[0].lower()}@dentalcare.com"
        mensaje += (
            f"ID:{id_doctor[i]} - Dr. {apellido} {nombre} - "
            f"{tratamientos_doctor[i]} - Usuario: {email}\n"
        )
    messagebox.showinfo("Doctores", mensaje if mensaje else "No hay doctores registrados.")

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
        messagebox.showerror("Error", "Usuario o clave incorrecta")
        return

    login_win.destroy()
    root.title(f"Sistema DentalCare - Usuario: {usuario_actual} ({perfil_actual})")
    root.deiconify()

    # Mostrar/ocultar botones según perfil - MODIFICACIÓN PRINCIPAL AQUÍ
    if perfil_actual == "medico":
        btn_ingresar_turno.config(state="disabled")
        btn_eliminar_turno.config(state="disabled")
        btn_agregar_doctor.config(state="disabled")
        btn_eliminar_doctor.config(state="disabled")
    elif perfil_actual == "paciente":
        # Paciente solo puede ingresar turno, ver y eliminar turno propio, no puede modificar doctores
        btn_ingresar_turno.config(state="normal")
        btn_eliminar_turno.config(state="normal")
        btn_agregar_doctor.config(state="disabled")
        btn_eliminar_doctor.config(state="disabled")
    else:
        # Admin y recepción pueden hacer todo
        btn_ingresar_turno.config(state="normal")
        btn_eliminar_turno.config(state="normal")
        btn_agregar_doctor.config(state="normal")
        btn_eliminar_doctor.config(state="normal")

# Ventana login
login_win = tk.Tk()
login_win.title("Login DentalCare")
login_win.geometry("300x180")

tk.Label(login_win, text="Usuario:").pack(pady=5)
entry_usuario = tk.Entry(login_win)
entry_usuario.pack()

tk.Label(login_win, text="Clave:").pack(pady=5)
entry_clave = tk.Entry(login_win, show="*")
entry_clave.pack()

btn_login = tk.Button(login_win, text="Ingresar", command=verificar_login)
btn_login.pack(pady=15)

# Ventana principal
root = tk.Tk()
root.title("Sistema DentalCare")
root.geometry("600x400")
root.withdraw()  # Oculta hasta login correcto

btn_ingresar_turno = tk.Button(root, text="Ingresar Turno", command=ingresar_turno)
btn_ver_turnos = tk.Button(root, text="Ver Turnos", command=ver_turnos)
btn_eliminar_turno = tk.Button(root, text="Eliminar Turno", command=eliminar_turno)
btn_agregar_doctor = tk.Button(root, text="Agregar Doctor", command=agregar_doctor)
btn_eliminar_doctor = tk.Button(root, text="Eliminar Doctor", command=eliminar_doctor)
btn_mostrar_doctores = tk.Button(root, text="Mostrar Doctores", command=mostrar_doctores)
btn_salir = tk.Button(root, text="Salir", command=salir)

botones = [
    btn_ingresar_turno,
    btn_ver_turnos,
    btn_eliminar_turno,
    btn_agregar_doctor,
    btn_eliminar_doctor,
    btn_mostrar_doctores,
    btn_salir,
]

for btn in botones:
    btn.pack(pady=5, fill='x', padx=20)

cargar_datos()



# ------------------ Función de registro de usuario -------------------
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
            datos_guardados.setdefault("doctores", {}).setdefault("Usuario", [])
            datos_guardados["doctores"].setdefault("Contraseña", [])
            if nuevo_usuario not in datos_guardados["doctores"]["Usuario"]:
                datos_guardados["doctores"]["Usuario"].append(nuevo_usuario)
                datos_guardados["doctores"]["Contraseña"].append(nueva_clave)

        elif perfil == "paciente":
            datos_guardados.setdefault("paciente", {}).setdefault("Usuario_socio", [])
            datos_guardados["paciente"].setdefault("Contraseña_socio", [])
            datos_guardados["paciente"].setdefault("ids_socio", [])

            nuevo_id = 1
            usados = set(datos_guardados["paciente"]["ids_socio"])
            while nuevo_id in usados:
                nuevo_id += 1

            datos_guardados["paciente"]["Usuario_socio"].append(nuevo_usuario)
            datos_guardados["paciente"]["Contraseña_socio"].append(nueva_clave)
            datos_guardados["paciente"]["ids_socio"].append(nuevo_id)

            usuarios[nuevo_usuario]["id"] = nuevo_id

            messagebox.showinfo(
                "Registrado",
                f"Usuario {nuevo_usuario} registrado con éxito.\nTu número de socio es: {nuevo_id}\n¡Guárdalo para pedir turnos!"
            )

        guardar_datos()
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

btn_registro = tk.Button(login_win, text="Registrarse", command=registrar_usuario)
btn_registro.pack()
login_win.mainloop()
root.mainloop()
