from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField, SubmitField, DateField, BooleanField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Length, NumberRange
# Importamos los controladores analizados del nuevo models.py basado en CSV
from models import SalonCSV, RegistroCSV

class RegistroForm(FlaskForm):
    """Formulario para registro de acudientes e hijos"""
    nombre_hijo = StringField('Nombre del Hijo', validators=[DataRequired(), Length(min=2, max=50)])
    edad_hijo = IntegerField('Edad del Hijo', validators=[DataRequired(), NumberRange(min=1, max=18)])
    nombre_acudiente = StringField('Nombre Completo del acudiente', validators=[DataRequired(), Length(min=3, max=50)])
    celular_acudiente = StringField('Celular del acudiente', validators=[DataRequired(), Length(min=7, max=20)])
    submit = SubmitField('Registrar')

class CambiarResponsableForm(FlaskForm):
    """Formulario para cambiar el responsable del salón"""
    nuevo_encargado = StringField('Nuevo Responsable', validators=[DataRequired(), Length(min=3, max=50)])
    submit = SubmitField('Actualizar Responsable')

class CambiarContraseñaForm(FlaskForm):
    """Formulario para cambiar el responsable del salón"""
    contrasena = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirmacion = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('contrasena', message='Las contraseñas no coinciden')])
    submit = SubmitField('Actualizar Contraseña')

class FechaForm(FlaskForm):
    """Formulario para cambiar el responsable del salón"""
    #Formato fecha "%Y-%m-%d" y que no sean obligatorios
    año = IntegerField('Año', validators=[NumberRange(min=1900, max=5000)], render_kw={"placeholder": "YYYY"})
    mes = IntegerField('Mes', validators=[NumberRange(min=1, max=12)], render_kw={"placeholder": "MM"})
    dia = IntegerField('Día', validators=[NumberRange(min=1, max=31)], render_kw={"placeholder": "DD"})
    submit = SubmitField('Obtener Registros')

class AñoForm(FlaskForm):
    """Formulario para cambiar el responsable del salón"""
    #Formato fecha "%Y-%m-%d" y que no sean obligatorios
    año = IntegerField('Año', validators=[NumberRange(min=1900, max=5000)], render_kw={"placeholder": "YYYY"})
    submit = SubmitField('Obtener Registros')

class MesForm(FlaskForm):
    """Formulario para cambiar el responsable del salón"""
    #Formato fecha "%Y-%m-%d" y que no sean obligatorios
    año = IntegerField('Año', validators=[NumberRange(min=1900, max=5000)], render_kw={"placeholder": "YYYY"})
    mes = IntegerField('Mes', validators=[NumberRange(min=1, max=12)], render_kw={"placeholder": "MM"})
    submit = SubmitField('Obtener Registros')

class SalonForm(FlaskForm):
    """Formulario para registro de salones"""
    nombre = StringField('Nombre del Salón', validators=[DataRequired(), Length(min=2, max=50)])
    usuario = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=50)])
    contrasena = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirmacion = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('contrasena', message='Las contraseñas no coinciden')])
    es_supervisor = BooleanField('supervisor')
    submit = SubmitField('Crear Usuario')

    def validate_usuario(self, usuario):
        salon = SalonCSV.filter_by_usuario(usuario.data)
        
        if salon:
            raise ValidationError('El usuario ya está registrado.')
class SalonLoginForm(FlaskForm):
    """Formulario para login de salones"""
    usuario = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=50)])
    contrasena = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Ingresar')