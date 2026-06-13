import os
import csv
from werkzeug.security import generate_password_hash
# Importamos las rutas de archivos y funciones necesarias desde el nuevo models
from models import CSV_SALON, CSV_REGISTRO, init_csv_files, SalonCSV

# Aseguramos que el directorio y los archivos base existan antes de insertar
init_csv_files()

if SalonCSV.get_all_admin() == []:
    print("--- CREACIÓN DE SALÓN ADMINISTRADOR ---")
    nombre = input("Nombre: ")
    usuario = input("Usuario: ")

    contrasena = "A"
    contrasena_2 = "B"

    while contrasena != contrasena_2:
        contrasena = input("Contraseña: ")
        contrasena_2 = input("Contraseña confirmación: ")

    try:
        # 1. Validar si el usuario ya existe en el archivo CSV
        if SalonCSV.filter_by_usuario(usuario):
            print(f"Error: El usuario '{usuario}' ya está registrado.")
            exit()

        # 2. Calcular el siguiente ID autoincremental de forma segura
        salones_existentes = SalonCSV.get_all()
        next_id = max([int(s.id) for s in salones_existentes], default=0) + 1

        # 3. Encriptar la contraseña de forma manual
        contrasena_hash = generate_password_hash(contrasena)

        # 4. Escribir la nueva fila en el archivo CSV con 'True' en es_admin
        with open(CSV_SALON, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([next_id, nombre, usuario, contrasena_hash, None, 'True', 'False', None])

        print(f"\n¡Éxito! El administrador '{usuario}' ha sido creado correctamente en el archivo CSV.")

    except Exception as e:
        print(f"Ocurrió un error inesperado al escribir en la base de datos CSV: {e}")

exit()