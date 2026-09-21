from datetime import date
import os
from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ba2e18ce248bab7ce9425333f0420b57a5f07dfef342e1876d3013a524acf416f813af3071a65e3860475fe8e81c3a42c3c8fa65051de39aa2037fa695b305a7bc7044a415eb'
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://neondb_owner:npg_fRPFDKrC15uw@ep-dark-heart-awmbb02x-pooler.c-12.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELOS SQL CON SQLALCHEMY ---

class Salon(db.Model, UserMixin):
    __tablename__ = 'salones'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    usuario = db.Column(db.String(100), nullable=False, unique=True)
    contrasena_hash = db.Column(db.String(255), nullable=False)
    encargado = db.Column(db.String(100), nullable=True)
    es_admin = db.Column(db.Boolean, nullable=False, default=False)
    es_supervisor = db.Column(db.Boolean, nullable=False, default=False)
    id_supervisor = db.Column(db.Integer, db.ForeignKey('salones.id'), nullable=True)

    supervisees = db.relationship('Salon', remote_side=[id], backref='supervisor_room', lazy='select')

    def check_password(self, password):
        return check_password_hash(self.contrasena_hash, password)

    def set_password(self, password):
        self.contrasena_hash = generate_password_hash(password)

class Registro(db.Model):
    __tablename__ = 'registros'

    id = db.Column(db.Integer, primary_key=True)
    nombre_hijo = db.Column(db.String(100), nullable=False)
    edad_hijo = db.Column(db.Integer, nullable=False)
    nombre_acudiente = db.Column(db.String(100), nullable=False)
    celular_acudiente = db.Column(db.String(50), nullable=False)
    salon_id = db.Column(db.Integer, db.ForeignKey('salones.id'), nullable=False)
    nombre_staff = db.Column(db.String(100), nullable=True)
    supervisor = db.Column(db.String(100), nullable=True)
    nombre_salon = db.Column(db.String(100), nullable=True)
    fecha_registro = db.Column(db.Date, nullable=False, default=date.today)
    entrada = db.Column(db.Boolean, nullable=False, default=True)
    salida = db.Column(db.Boolean, nullable=False, default=False)

    salon = db.relationship('Salon', backref='registros', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'nombre_hijo': self.nombre_hijo,
            'edad_hijo': self.edad_hijo,
            'nombre_acudiente': self.nombre_acudiente,
            'celular_acudiente': self.celular_acudiente,
            'salon_id': self.salon_id,
            'nombre_staff': self.nombre_staff,
            'supervisor': self.supervisor,
            'nombre_salon': self.nombre_salon,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'entrada': self.entrada,
            'salida': self.salida
        }

# --- CONTROLADORES DE ACCESO SQL ---

class SalonCSV:
    @staticmethod
    def get(id):
        if id is None:
            return None
        return Salon.query.get(int(id))

    @staticmethod
    def filter_by_usuario(usuario):
        return Salon.query.filter_by(usuario=usuario).first()

    @staticmethod
    def get_all_admin():
        return Salon.query.filter_by(es_admin=True).all()

    @staticmethod
    def get_all_salones():
        return Salon.query.filter_by(es_supervisor=False, es_admin=False).all()

    @staticmethod
    def get_all_salones_by_supervisor(id_supervisor):
        return Salon.query.filter_by(es_supervisor=False, es_admin=False, id_supervisor=id_supervisor).all()

    @staticmethod
    def get_all_supervisores():
        return Salon.query.filter_by(es_supervisor=True).all()

    @staticmethod
    def get_all():
        return Salon.query.all()

    @staticmethod
    def add(nombre, usuario, contrasena, es_supervisor=False, es_admin=False):
        if SalonCSV.filter_by_usuario(usuario):
            raise Exception("El usuario ya existe")

        salon = Salon(
            nombre=nombre,
            usuario=usuario,
            contrasena_hash=generate_password_hash(contrasena),
            encargado=None,
            es_admin=bool(es_admin),
            es_supervisor=bool(es_supervisor),
            id_supervisor=None
        )
        db.session.add(salon)
        db.session.commit()
        return salon

    @staticmethod
    def delete(id_salon):
        salon = Salon.query.get(id_salon)
        if not salon:
            raise Exception('Salón no encontrado')
        if Registro.query.filter_by(salon_id=salon.id).first():
            raise Exception('No se puede eliminar un salón que tiene registros')
        db.session.delete(salon)
        db.session.commit()

    @staticmethod
    def update_password(id_salon, new_password):
        salon = Salon.query.get(id_salon)
        if not salon:
            raise Exception('Salón no encontrado')
        salon.contrasena_hash = generate_password_hash(new_password)
        db.session.commit()

    @staticmethod
    def update_encargado(id_salon, nuevo_encargado):
        salon = Salon.query.get(id_salon)
        if not salon:
            raise Exception('Salón no encontrado')
        salon.encargado = nuevo_encargado
        db.session.commit()

    @staticmethod
    def update_supervisor(id_salon, id_supervisor):
        salon = Salon.query.get(id_salon)
        if not salon:
            raise Exception('Salón no encontrado')
        salon.id_supervisor = id_supervisor
        db.session.commit()

SalonUser = Salon

class RegistroCSV:
    @staticmethod
    def add(nombre_hijo, edad_hijo, nombre_acudiente, celular_acudiente, salon_id):
        salon = SalonCSV.get(salon_id)
        if not salon:
            raise Exception('Salón no encontrado')

        nombre_staff = salon.encargado or 'Desconocido'
        nombre_salon = salon.nombre
        supervisor_text = None
        if salon.id_supervisor:
            supervisor = SalonCSV.get(salon.id_supervisor)
            supervisor_text = supervisor.encargado if supervisor else None

        registro = Registro(
            nombre_hijo=nombre_hijo,
            edad_hijo=edad_hijo,
            nombre_acudiente=nombre_acudiente,
            celular_acudiente=celular_acudiente,
            salon_id=salon.id,
            nombre_staff=nombre_staff,
            supervisor=supervisor_text,
            nombre_salon=nombre_salon,
            fecha_registro=date.today(),
            entrada=True,
            salida=False
        )
        db.session.add(registro)
        db.session.commit()
        return registro.id

    @staticmethod
    def get_registros_by_salon_id(salon_id):
        today = date.today()
        registros = Registro.query.filter_by(salon_id=salon_id, salida=False).filter(Registro.fecha_registro == today).order_by(Registro.nombre_hijo).all()
        return [registro.to_dict() for registro in registros]

    @staticmethod
    def marcar_salida(registro_id):
        registro = Registro.query.get(registro_id)
        if not registro:
            raise Exception('Registro no encontrado')

        registro.salida = True
        salon = SalonCSV.get(registro.salon_id)
        registro.nombre_staff = salon.encargado or 'Desconocido'
        db.session.commit()

    @staticmethod
    def get_registros_for_report(anio, mes=None, dia=None, salon_id=None):
        from sqlalchemy import extract

        query = Registro.query
        if salon_id is not None:
            query = query.filter_by(salon_id=salon_id)

        if anio is not None:
            query = query.filter(extract('year', Registro.fecha_registro) == anio)
        if mes is not None:
            query = query.filter(extract('month', Registro.fecha_registro) == mes)
        if dia is not None:
            query = query.filter(extract('day', Registro.fecha_registro) == dia)

        registros = query.order_by(Registro.fecha_registro, Registro.nombre_hijo).all()
        return [registro.to_dict() for registro in registros]
