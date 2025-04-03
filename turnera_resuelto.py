# Esta es una resolución de las muchas formas que puede hacerse. Aprovecho para mostrarles muchas funciones y como reutilizarlas.

# DEFINICION DE FUNCIONES

def menu():
    print("\nMenú del sistema")
    print("\t1. Ingresar turnos")
    print("\t2. Ver turnos")
    print("\t3. Eliminar turnos cancelados")
    print("\t4. Agregar doctor")
    print("\t5. Eliminar doctor")
    print("\t6. salir")

    opcion = int(input("\nIngrese opción 1 a 6: "))
    while opcion < 1 or opcion > 6:
        print("Opción no valida")
        opcion = int(input("\nIngrese opción 1 a 6: "))

    return opcion

def agregar_doctor(id_lista, nombres, apellidos, tratamientos):
    id = ingresar_id(id_lista)
    nombre = ingresar_nombre()
    apellido = ingresar_apellido()
    tratamiento = ingresar_tratamiento(TRATAMIENTOS)

    id_lista.append(id)
    nombres.append(nombre)
    apellidos.append(apellido)
    tratamientos.append(tratamiento)

    return "Doctor agregado correctamente."

def eliminar_doctor(id_lista, nombres, apellidos, tratamientos):
    if not id_lista:
        return "No hay doctores registrados."

    id_eliminar = int(input("Ingrese el ID del doctor a eliminar: "))

    if id_eliminar in id_lista:
        indice = id_lista.index(id_eliminar)

        id_lista.pop(indice)
        nombres.pop(indice)
        apellidos.pop(indice)
        tratamientos.pop(indice)

        return f"Doctor con ID {id_eliminar} eliminado correctamente."
    else:
        return "El ID ingresado no existe."
    

def ingresar_turnos(nombres, numeros_socios, horarios, tratamientos, tratamiento_opciones, turnos_maximos, hora_desde, hora_hasta):

    if len(nombres) < turnos_maximos:
        numero_socio = ingresar_socio()
        if buscar(numero_socio, numeros_socios) != -1:
            return "El socio ya dispone de un turno. Utilice la opcion 2 del menu para verlo u opcion 3 para eliminarlo."
        
        nombre = ingresar_nombre()
        horario = ingresar_horario(horarios, hora_desde, hora_hasta)
        tratamiento = ingresar_tratamiento(tratamiento_opciones)
    else:
        return "No hay turnos disponibles"
    
    nombres.append(nombre)
    numeros_socios.append(numero_socio)
    horarios.append(horario)
    tratamientos.append(tratamiento)
    return "Turno guardado correctamente"

def mostrar_turnos(nombres, numeros_socios, horarios, tratamientos, tratamiento_opciones):
    if not nombres:
        return "No hay turnos registrados."

    print("\nLista de turnos:")
    for i in range(len(nombres)):
        print(f"{i+1}. {nombres[i]} - Socio: {numeros_socios[i]} - Horario: {horarios[i]} hs - Tratamiento: {tratamiento_opciones[tratamientos[i]]}")

    return "Turnos mostrados correctamente."


def ingresar_nombre():
    nombre = input("\nIngrese nombre del paciente: ")
    while nombre == '':
        print("El nombre no puede estar vacío.")
        nombre = input("\nIngrese nombre del paciente: ")
        
    return nombre

def ingresar_apellido():
    apellido = input("\nIngrese apellido del doctor: ")
    while apellido == '':
        print("El apellido no puede estar vacío.")
        apellido = input("\nIngrese apellido del doctor: ")
    return apellido


def ingresar_id(id_lista):
    if not id_lista:
        return 1  

    id_lista.sort() 

    for i in range(1, id_lista[-1] + 2):  
        if i not in id_lista:
            return i



def ingresar_socio():
    numero_socio = int(input("Ingrese número de socio del paciente: "))
    while numero_socio < 1:
        print("El numero de socio no puede ser 0 o negativo o ya existir.")
        numero_socio = int(input("\nIngrese número de socio del paciente: "))
    
    return numero_socio


def ingresar_horario(horarios, hora_desde, hora_hasta):
    horario = float(input("Ingrese el horario (ej: 8, 9.30): "))
    while validar_horario(horario, hora_desde, hora_hasta) or horario in horarios:
        print("Turno inválido u ocupado")
        horario = float(input("\nIngrese el horario (ej: 8, 9.30): "))
    return horario



def ingresar_tratamiento(tratamiento_opciones):
    print("Seleccione un tratamiento: ")
    for i, tratamiento in enumerate(tratamiento_opciones, 1):
        print(f"\t{i}. {tratamiento}")

    opcion = int(input(f"Ingrese opción 1 a {len(tratamiento_opciones)}: "))
    while opcion < 1 or opcion > len(tratamiento_opciones):
        print("Opción no válida")
        opcion = int(input(f"Ingrese opción 1 a {len(tratamiento_opciones)}: "))

    return tratamiento_opciones[opcion - 1]  # Guardamos el nombre, no el índice



def intercambiar(arreglo, i, j):
    aux = arreglo[j]
    arreglo[j] = arreglo[i]
    arreglo[i] = aux


def validar_horario(horario, hora_desde, hora_hasta):
    '''Verifica que la hora sea entre el rango desde y hasta, y que sea cada 30 minutos. Retorna False si es valido'''
    if horario >= hora_desde and horario <= hora_hasta: #primero horario debe estar en el rango de 8 a 20
        # establezco que los turnos son cada 30 minutos. Este requisito es opcional
        z = int((horario-int(horario))*100)
        # si el horario es 9.25, 9.30, 9, etc, horario - int(horario) deberia dar 0.25, 0.30, 0.0, etc (respectivamente)
        # pero python tiene un tema con la representacion de decimales, entonces, hago la resta, multiplico por 100 para que quede 30.x, 25.x, lo y lo convierto a entero. De esa forma z será 0, 10, 25, 30, etc. segun los 'minutos'
        if z == 0 or z == 30: # en punto o y media
            return False
        
    return True # true para que siga el while ya que no cumple ni el rango ni los minutos


def eliminar_turno(nombres, numeros_socios, horarios, tratamientos):
    socio = ingresar_socio()
    indice = buscar(socio, numeros_socios) 
    if indice == -1:
        return "El número de socio ingresado no registra turno en este consultorio."
    
    nombre = nombres.pop(indice)
    numero_socio = numeros_socios.pop(indice)
    horario = horarios.pop(indice)
    tratamientos.pop(indice)

    return(f"Se eliminó correctamente el turno para las {horario} hs. correspondiente a {nombre} (Nº/S: {numero_socio})")




def buscar(item, arreglo):
    '''Busca un item dentro de un arreglo. Retorna -1 si no lo encuentra o el indice'''
    i = 0   
    while(i < len(arreglo) and item != arreglo[i]):
        i+=1

    if i == len(arreglo):
        return -1
    return i


def calcular_cantidad_pacientes(horarios, hora):
    cont = 0
    for i in range(len(horarios)):
        if horarios[i] < hora:
            cont += 1
    
    return cont


# DECLARACION DE CONSTANTES PARA EL MAIN
TRATAMIENTOS = ['Control', 'Arreglo de caries', 'Ortodoncia', 'Extracción']
TURNOS_MAXIMOS = 23
APERTURA = 8 # horas
CIERRE = 20 # horas


# DECLARACION DE VARIABLES PARA EL MAIN
nombres = []
numeros_socios = []
horarios = []
tratamientos = []
id_lista=[]
apellidos=[]


# PROGRAMA MAIN (PRINCIPAL)
opcion = menu()
while opcion != 6:

    if opcion == 1:
        mensaje = ingresar_turnos(nombres, numeros_socios, horarios, tratamientos, TRATAMIENTOS, TURNOS_MAXIMOS, APERTURA, CIERRE)

    if opcion == 2:
        mensaje = mostrar_turnos(nombres, numeros_socios, horarios, tratamientos, TRATAMIENTOS)

    if opcion == 3:
        mensaje = eliminar_turno(nombres, numeros_socios, horarios, tratamientos)

    if opcion == 4:
        mensaje = agregar_doctor(id_lista, nombres, apellidos, tratamientos)

    if opcion == 5:
        mensaje = eliminar_doctor(id_lista, nombres, apellidos, tratamientos)

    print(mensaje)
    opcion = menu()

print("\nPrograma finalizado por el usuario cuando ingresó 6.")
