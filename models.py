from datetime import datetime
import os
import csv
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask
from flask_login import UserMixin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ba2e18ce248bab7ce9425333f0420b57a5f07dfef342e1876d3013a524acf416f813af3071a65e3860475fe8e81c3a42c3c8fa65051de39aa2037fa695b305a7bc7044a415eb'
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Rutas de los archivos CSV que actuarán como tablas
DATA_DIR = "DB"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

CSV_SALON = os.path.join(DATA_DIR, "Salones.csv")
CSV_REGISTRO = os.path.join(DATA_DIR, f"Registro-{datetime.now().strftime('%Y')}.csv")

# Inicializar archivos con sus cabeceras correspondientes
def init_csv_files():
    if not os.path.exists(CSV_SALON):
        with open(CSV_SALON, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'nombre', 'usuario', 'contrasena_hash', 'encargado', 'es_admin', 'es_supervisor', 'id_supervisor'])
            
    if not os.path.exists(CSV_REGISTRO):
        with open(CSV_REGISTRO, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'nombre_hijo', 'edad_hijo', 'nombre_acudiente', 'celular_acudiente', 'salon_id', 'nombre_staff', 'supervisor', 'nombre_salon', 'fecha_registro', 'entrada', 'salida'])

init_csv_files()

# --- CLASES AUXILIARES COMPATIBLES CON FLASK-LOGIN ---

class SalonUser(UserMixin):
    def __init__(self, id, nombre, usuario, contrasena_hash, encargado, es_admin, es_supervisor, id_supervisor):
        self.id = str(id)
        self.nombre = nombre
        self.usuario = usuario
        self.contrasena_hash = contrasena_hash
        self.encargado = encargado
        self.es_admin = es_admin
        self.es_supervisor = es_supervisor
        self.id_supervisor = id_supervisor

    def check_password(self, password):
        return check_password_hash(self.contrasena_hash, password)
    
    def set_password(self, contrasena_hash):
        self.contrasena_hash = generate_password_hash(contrasena_hash)

# --- CONTROLADORES DE ACCESO MANUAL (MOCK DE CONSULTAS) ---

class SalonCSV:
    @staticmethod
    def get(id):
        with open(CSV_SALON, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['id'] == str(id):
                    return SalonUser(row['id'], row['nombre'], row['usuario'], row['contrasena_hash'], row['encargado'], row['es_admin'], row['es_supervisor'], row['id_supervisor'])
        return None

    @staticmethod
    def filter_by_usuario(usuario):
        with open(CSV_SALON, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['usuario'] == usuario:
                    return SalonUser(row['id'], row['nombre'], row['usuario'], row['contrasena_hash'], row['encargado'], row['es_admin'], row['es_supervisor'], row['id_supervisor'])
        return None
    
    @staticmethod
    def get_all_admin():
        salones = []
        with open(CSV_SALON, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['es_admin'] == 'True':
                    salones.append(SalonUser(row['id'], row['nombre'], row['usuario'], row['contrasena_hash'], row['encargado'], row['es_admin'], row['es_supervisor'], row['id_supervisor']))
        return salones
    
    @staticmethod
    def get_all_salones():
        salones = []
        with open(CSV_SALON, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['es_supervisor'] == 'False' and row['es_admin'] == 'False':
                    salones.append(SalonUser(row['id'], row['nombre'], row['usuario'], row['contrasena_hash'], row['encargado'], row['es_admin'], row['es_supervisor'], row['id_supervisor']))
        return salones
    
    @staticmethod
    def get_all_salones_by_supervisor(id_supervisor):
        salones = []
        with open(CSV_SALON, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['es_supervisor'] == 'False' and row['es_admin'] == 'False' and row['id_supervisor'] == id_supervisor:
                    salones.append(SalonUser(row['id'], row['nombre'], row['usuario'], row['contrasena_hash'], row['encargado'], row['es_admin'], row['es_supervisor'], row['id_supervisor']))
        return salones
    
    @staticmethod
    def get_all_supervisores():
        salones = []
        with open(CSV_SALON, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['es_supervisor'] == 'True':
                    salones.append(SalonUser(row['id'], row['nombre'], row['usuario'], row['contrasena_hash'], row['encargado'], row['es_admin'], row['es_supervisor'], row['id_supervisor']))
        return salones

    @staticmethod
    def get_all():
        salones = []
        with open(CSV_SALON, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                salones.append(SalonUser(row['id'], row['nombre'], row['usuario'], row['contrasena_hash'], row['encargado'], row['es_admin'], row['es_supervisor'], row['id_supervisor']))
        return salones

    @staticmethod
    def add(nombre, usuario, contrasena, es_supervisor=False):
        # Autoincrementar ID
        rows = SalonCSV.get_all()
        next_id = max([int(r.id) for r in rows], default=0) + 1

        # Validar duplicados
        if SalonCSV.filter_by_usuario(usuario):
            raise Exception("El usuario ya existe")

        hash_p = generate_password_hash(contrasena)

        with open(CSV_SALON, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                next_id, 
                nombre, 
                usuario, 
                hash_p, 
                None,              # Campo vacío (ej. token o descripción)
                'False',         # ¿Es administrador global? False
                es_supervisor,    # Aquí entra True o False dinámicamente
                None
            ])

    @staticmethod
    def delete(id_salon):
        rows = []
        with open(CSV_SALON, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = [row for row in reader if row['id'] != str(id_salon)]
            
        with open(CSV_SALON, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'nombre', 'usuario', 'contrasena_hash', 'encargado', 'es_admin', 'es_supervisor', 'id_supervisor'])
            for r in rows:
                writer.writerow([r['id'], r['nombre'], r['usuario'], r['contrasena_hash'], r['encargado'], r['es_admin'], r['es_supervisor'], r['id_supervisor']])

    @staticmethod
    def update_password(id_salon, new_password):
        rows = []
        with open(CSV_SALON, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = [row for row in reader]

        for row in rows:
            if row['id'] == str(id_salon):
                row['contrasena_hash'] = generate_password_hash(new_password)

        with open(CSV_SALON, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'nombre', 'usuario', 'contrasena_hash', 'encargado', 'es_admin', 'es_supervisor', 'id_supervisor'])
            for r in rows:
                writer.writerow([r['id'], r['nombre'], r['usuario'], r['contrasena_hash'], r['encargado'], r['es_admin'], r['es_supervisor'], r['id_supervisor']])

    @staticmethod
    def update_encargado(id_salon, nuevo_encargado):
        rows = []
        with open(CSV_SALON, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = [row for row in reader]

        for row in rows:
            if row['id'] == str(id_salon):
                row['encargado'] = nuevo_encargado

        with open(CSV_SALON, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'nombre', 'usuario', 'contrasena_hash', 'encargado', 'es_admin', 'es_supervisor', 'id_supervisor'])
            for r in rows:
                writer.writerow([r['id'], r['nombre'], r['usuario'], r['contrasena_hash'], r['encargado'], r['es_admin'], r['es_supervisor'], r['id_supervisor']])

    @staticmethod
    def update_supervisor(id_salon, id_supervisor):
        rows = []
        with open(CSV_SALON, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = [row for row in reader]

        for row in rows:
            if row['id'] == str(id_salon):
                row['id_supervisor'] = id_supervisor

        with open(CSV_SALON, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'nombre', 'usuario', 'contrasena_hash', 'encargado', 'es_admin', 'es_supervisor', 'id_supervisor'])
            for r in rows:
                writer.writerow([r['id'], r['nombre'], r['usuario'], r['contrasena_hash'], r['encargado'], r['es_admin'], r['es_supervisor'], r['id_supervisor']])

class RegistroCSV:
    @staticmethod
    def add(nombre_hijo, edad_hijo, nombre_acudiente, celular_acudiente, salon_id):
        # Autoincrementar ID
        with open(CSV_REGISTRO, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            next_id = max([int(r['id']) for r in rows], default=0) + 1

        with open(CSV_REGISTRO, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            salon = SalonCSV.get(salon_id)
            nombre_staff = salon.encargado if salon.encargado != '' else 'Desconocido'
            nombre_salon = salon.nombre if salon else 'Salón no encontrado'
            supervisor = SalonCSV.get(salon.id_supervisor).encargado
            entrada = True
            salida = False
            writer.writerow([next_id, nombre_hijo, edad_hijo, nombre_acudiente, celular_acudiente, salon_id, nombre_staff, supervisor, nombre_salon, datetime.now().strftime("%Y-%m-%d"), entrada, salida])

        return next_id
    #Obtener registros por salon_id de la fecha actual
    @staticmethod
    def get_registros_by_salon_id(salon_id):
        registros = []
        with open(CSV_REGISTRO, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['salon_id'] == str(salon_id) and row['fecha_registro'] == datetime.now().strftime("%Y-%m-%d") and row['salida'] == 'False':
                    registros.append(row)
        # Ordenar alfabéticamente por nombre del hijo
        registros.sort(key=lambda x: x['nombre_hijo'].lower())
        return registros
    
    @staticmethod
    def marcar_salida(registro_id):
        rows = []
        with open(CSV_REGISTRO, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = [row for row in reader]

        for row in rows:
            if row['id'] == str(registro_id):
                row['salida'] = True
                salon = SalonCSV.get(row['salon_id'])
                row['nombre_staff'] = salon.encargado if salon.encargado != '' else 'Desconocido'

        with open(CSV_REGISTRO, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'nombre_hijo', 'edad_hijo', 'nombre_acudiente', 'celular_acudiente', 'salon_id', 'nombre_staff', 'encargado', 'nombre_salon', 'fecha_registro', 'entrada', 'salida'])
            for r in rows:
                writer.writerow([r['id'], r['nombre_hijo'], r['edad_hijo'], r['nombre_acudiente'], r['celular_acudiente'], r['salon_id'], r['nombre_staff'],r['encargado'], r['nombre_salon'], r['fecha_registro'], r['entrada'], r['salida']])