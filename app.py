from flask import abort, render_template, redirect, url_for, request, flash, send_file
from flask_login import LoginManager, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash
from datetime import timedelta
# Importamos las clases CSV simuladas
from models import RegistroCSV, app, SalonCSV, SalonUser, CSV_REGISTRO
from forms import SalonLoginForm, SalonForm, RegistroForm, CambiarResponsableForm, CambiarContraseñaForm, FechaForm, AñoForm, MesForm

import io
import pandas as pd

# Cache buster - forces template reload
_CACHE_BUSTER = "v2"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "main"


@login_manager.user_loader
def load_user(user_id):
    return SalonCSV.get(user_id)


@app.route("/", methods=["GET"])
def main():
    return render_template("main.jinja2")

#-------------------------------------------
# Registro
#-------------------------------------------

@app.route("/salones/", methods=["GET", "POST"])
def salones():
    salones = SalonCSV.get_all_salones()
    if request.method == 'POST':
        try:
            salon_id = int(request.form['salon'])
            return redirect(url_for("salon_home", salon_id=salon_id))
        except:
            flash("Error al asignar el salón. Intenta de nuevo", "error")
    return render_template("registro/asignacion.jinja2", salones=salones)

@app.route("/salon/<int:salon_id>", methods=["GET", "POST"])
def salon_home(salon_id):
    salon = SalonCSV.get(salon_id)
    if not salon:
        return redirect(url_for("salones"))
    if salon.es_admin == 'True':
        flash("No puedes registrar un hijo en un salón administrativo. Por favor selecciona otro salón.", "error")
        return redirect(url_for("salones"))
    if salon.es_supervisor == 'True':
        flash("No puedes registrar un hijo en un salón administrativo. Por favor selecciona otro salón.", "error")
        return redirect(url_for("salones"))
    if request.method == 'POST':
        try:
            nombre = request.form['nombre_hijo']
            edad = int(request.form['edad_hijo'])
            nombre_acudiente = request.form['nombre_acudiente']
            celular_acudiente = request.form['celular_acudiente']
            Registro = RegistroCSV.add(nombre_hijo=nombre, edad_hijo=edad, nombre_acudiente=nombre_acudiente, celular_acudiente=celular_acudiente, salon_id=salon_id)
            return redirect(url_for("scarapela", salon_id=salon_id, nombre_salon=salon.nombre, nombre_hijo=nombre, edad_hijo=edad, codigo_registro=Registro))
        except Exception as e:
            flash(str(e) if "existe" in str(e) else "Error en el registro. Intenta de nuevo", "error")
    return render_template("registro/FormRegistroHijos.jinja2", form=RegistroForm(), salon=salon)

@app.route("/RegistroExitoso", methods=["GET"])
def scarapela():
    salon_id = request.args.get('salon_id', type=int)
    nombre_hijo = request.args.get('nombre_hijo')
    edad_hijo = request.args.get('edad_hijo', type=int)
    Registro = request.args.get('codigo_registro', type=int)
    nombre_salon = SalonCSV.get(salon_id).nombre if salon_id and SalonCSV.get(salon_id) else "Salón no encontrado"
    return render_template("registro/Scarapela.jinja2", salon_id=salon_id, nombre_salon=nombre_salon, nombre_hijo=nombre_hijo, edad_hijo=edad_hijo, codigo_registro=Registro)

#Marcar salida del hijo
@app.route("/staff/<int:salon_id>/salida/<int:registro_id>", methods=["POST", "GET"])
def marcar_salida(salon_id, registro_id):
    try:
        RegistroCSV.marcar_salida(registro_id)
        flash("Salida marcada correctamente", "success")
    except Exception as e:
        flash("Error al marcar la salida. Intenta de nuevo", "error")
    return redirect(url_for("staff_home"))

@app.route("/staff/<int:salon_id>/responsable", methods=["GET", "POST"])
def cambiar_responsable(salon_id):
    form = CambiarResponsableForm()
    if request.method == 'POST':
        try:
            nuevo_encargado = request.form['nuevo_encargado']
            SalonCSV.update_encargado(salon_id, nuevo_encargado)
            flash("Responsable actualizado correctamente", "success")
            if current_user.es_supervisor == 'True':
                return redirect(url_for("staff_supervisor_home"))
            if current_user.es_supervisor == 'False':
                return redirect(url_for("staff_home"))
        except Exception as e:
            flash("Error al actualizar el responsable. Intenta de nuevo", "error")
    return render_template("staff/cambiar_responsable.jinja2", salon_id=salon_id, form=form)

@app.route("/admin/<int:salon_id>/Contrasena", methods=["GET", "POST"])
def cambiar_Contraseña(salon_id):
    form = CambiarContraseñaForm()
    if request.method == 'POST':
        try:
            contrasena = request.form['contrasena']
            SalonCSV.update_password(salon_id, contrasena)
            flash("Contraseña actualizada", "success")
            return redirect(url_for("staff_admin_home"))
        except Exception as e:
            flash("Error al actualizar el responsable. Intenta de nuevo", "error")
    return render_template("staff/cambiar_contraseña.jinja2", salon_id=salon_id, form=form)

@app.route("/staff-admin/<int:salon_id>/supervisor", methods=["GET", "POST"])
def añadir_supervisor(salon_id):
    salones = SalonCSV.get_all_supervisores()
    if request.method == 'POST':
        try:
            supervisor_id = int(request.form['salon'])
            print(supervisor_id)
            SalonCSV.update_supervisor(salon_id, supervisor_id)
            return redirect(url_for("staff_admin_home", salon_id=salon_id))
        except:
            flash("Error al asignar el salón. Intenta de nuevo", "error")
    return render_template("staff/asignacion _supervisor.jinja2", salones=salones)

#-------------------------------------------
# Staff
#-------------------------------------------

@app.route("/staff/home", methods=["GET"])
def staff_home():
    if not current_user.is_authenticated:
        return redirect(url_for("staff_logIn"))
    id_salon = current_user.id
    responsable = SalonCSV.get(id_salon).encargado if SalonCSV.get(id_salon) else "Desconocido"
    estudiantes = RegistroCSV.get_registros_by_salon_id(id_salon)
    return render_template("staff/home.jinja2", estudiantes=estudiantes, nombre=current_user.nombre, salon_id=id_salon, responsable=responsable)

@app.route("/staff-admin/home", methods=["GET"])
def staff_admin_home():
    if not current_user.is_authenticated or not current_user.es_admin:
        return redirect(url_for("staff_logIn"))
    id_salon = current_user.id
    return render_template("staff/admin.jinja2", salon_id=id_salon, salones=SalonCSV.get_all_salones(), supervisores=SalonCSV.get_all_supervisores())

@app.route("/staff-supervisor/home", methods=["GET"])
def staff_supervisor_home():
    if not current_user.is_authenticated or not current_user.es_supervisor:
        return redirect(url_for("staff_logIn"))
    id_salon = current_user.id
    responsable = SalonCSV.get(id_salon).encargado if SalonCSV.get(id_salon) else "Desconocido"
    return render_template("staff/supervisor.jinja2", salon_id=id_salon, responsable=responsable, supervisores=SalonCSV.get_all_salones_by_supervisor(id_salon))

@app.route("/staff/logIn", methods=["GET", "POST"])
def staff_logIn():
    form = SalonLoginForm()
    if form.validate_on_submit():
        salon = SalonCSV.filter_by_usuario(form.usuario.data)
        if salon and salon.check_password(form.contrasena.data):
            if salon.es_admin == 'True' and salon.es_supervisor == 'False':
                login_user(salon, remember=True, duration=timedelta(hours=3))
                return redirect(url_for("staff_admin_home"))
            elif salon.es_supervisor == 'True' and salon.es_admin == 'False':
                login_user(salon, remember=True, duration=timedelta(hours=3))
                return redirect(url_for("staff_supervisor_home"))
            elif salon.es_admin == 'False' and salon.es_supervisor == 'False':
                login_user(salon, remember=True, duration=timedelta(hours=3))
                return redirect(url_for("staff_home"))
        flash("Usuario o contraseña incorrectos", "error")
    return render_template("staff/ingreso.jinja2", form=form)

@app.route("/logout", methods=["GET"])
def staff_logout():
    logout_user()
    return redirect(url_for("staff_logIn"))

@app.route("/add-staff", methods=["GET", "POST"])
def add_staff():
    form = SalonForm()
    if form.validate_on_submit():
        try:
            nombre = form.nombre.data
            usuario = form.usuario.data
            contrasena = form.contrasena.data
            supervisor = form.es_supervisor.data
            SalonCSV.add(nombre=nombre, usuario=usuario, contrasena=contrasena, es_supervisor=supervisor)
            return redirect(url_for('staff_admin_home'))
        except Exception as e:
            flash(str(e) if "existe" in str(e) else "Error en el registro. Intenta de nuevo", "error")
            return render_template("staff/rejistro.jinja2", form=form)
    return render_template("staff/rejistro.jinja2", form=form)

@app.route("/staff-admin/Registro/<int:salon_id>/eliminar-salon", methods=["GET", "POST"])
def eliminar_salon(salon_id):
    try:
        SalonCSV.delete(salon_id)
    except:
        flash("Error al eliminar el hijo. Intenta de nuevo", "error")
    return render_template("staff/admin.jinja2", salones=SalonCSV.get_all_non_admin(), supervisores=SalonCSV.get_all_supervisores())

@app.route("/staff/Registro", methods=["GET", "POST"])
def staff_registro():
    form = SalonLoginForm()
    if form.validate_on_submit():
        try:
            SalonCSV.add(nombre=form.nombre.data, usuario=form.usuario.data, contrasena=form.contrasena.data)
            flash("Registro exitoso. Por favor ingresa con tu usuario y contraseña", "success")
            return redirect(url_for("staff_logIn"))
        except Exception as e:
            flash("Error en el registro o el usuario ya existe.", "error")
    return render_template("staff/registro.jinja2", form=form)

@app.route("/staff-admin/Registro/<int:salon_id>", methods=["GET", "POST"])
def staff_admin_registro(salon_id):
    form_dia = FechaForm()
    form_año = AñoForm()
    form_mes = MesForm()
    return render_template("staff/registros_fecha.jinja2", form_dia=form_dia, form_año=form_año, form_mes=form_mes, salon_id=salon_id)

# ==========================================
# 1. VARIANTE: EXCEL POR AÑO COMPLETO
# ==========================================
@app.route('/staff-admin/Registro/reporte/anio/<int:anio>/<int:salon_id>', methods=['GET'])
def descargar_reporte_anio(anio, salon_id):
    try:
        df = pd.read_csv(fr"DB\Registro-{anio}.csv")
        df['fecha_registro'] = pd.to_datetime(df['fecha_registro'])
        
        # Filtrar por año y por el salon_id
        df_filtrado = df[
            (df['fecha_registro'].dt.year == anio) & 
            (df['salon_id'] == salon_id)
        ]
        
        df_filtrado = df_filtrado.copy()
        df_filtrado['fecha_registro'] = df_filtrado['fecha_registro'].dt.strftime('%Y-%m-%d')
        
        # Para Excel usamos estrictamente BytesIO (no StringIO)
        buffer = io.BytesIO()
        
        # Guardamos en el buffer usando el motor openpyxl sin el índice de pandas
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_filtrado.to_excel(writer, index=False, sheet_name='Registros Anuales')
            
        buffer.seek(0)
        
        # Retornamos modificando el mimetype al estándar de Excel (.xlsx)
        return send_file(
            buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'registro_salon_{salon_id}_anio_{anio}.xlsx'
        )
    except FileNotFoundError:
        return abort(404, description="El archivo de registros no existe.")
    except Exception as e:
        return abort(500, description=str(e))


# ==========================================
# 2. VARIANTE: EXCEL POR MES COMPLETO
# ==========================================
@app.route('/staff-admin/Registro/reporte/mes/<int:anio>/<int:mes>/<int:salon_id>', methods=['GET'])
def descargar_reporte_mes(anio, mes, salon_id):
    try:
        df = pd.read_csv(fr"DB\Registro-{anio}.csv")
        df['fecha_registro'] = pd.to_datetime(df['fecha_registro'])
        
        # Filtrar por año, mes y salón
        df_filtrado = df[
            (df['fecha_registro'].dt.year == anio) & 
            (df['fecha_registro'].dt.month == mes) & 
            (df['salon_id'] == salon_id)
        ]
        
        df_filtrado = df_filtrado.copy()
        df_filtrado['fecha_registro'] = df_filtrado['fecha_registro'].dt.strftime('%Y-%m-%d')
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_filtrado.to_excel(writer, index=False, sheet_name='Registros Mensuales')
            
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'registro_salon_{salon_id}_mes_{anio}_{mes:02d}.xlsx'
        )
    except FileNotFoundError:
        return abort(404, description="El archivo de registros no existe.")
    except Exception as e:
        return abort(500, description=str(e))


# ==========================================
# 3. VARIANTE: EXCEL POR DIA / FECHA EXACTA
# ==========================================
@app.route('/staff-admin/Registro/reporte/dia/<int:anio>/<int:mes>/<int:dia>/<int:salon_id>', methods=['GET'])
def descargar_reporte_dia(anio, mes, dia, salon_id):
    try:
        df = pd.read_csv(fr"DB\Registro-{anio}.csv")
        fecha_busqueda = f"{anio}-{mes:02d}-{dia:02d}"
        
        # Filtrar fecha exacta y salón
        df_filtrado = df[
            (df['fecha_registro'] == fecha_busqueda) & 
            (df['salon_id'] == salon_id)
        ]
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_filtrado.to_excel(writer, index=False, sheet_name='Registros Diarios')
            
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'registro_salon_{salon_id}_dia_{fecha_busqueda}.xlsx'
        )
    except FileNotFoundError:
        return abort(404, description="El archivo de registros no existe.")
    except Exception as e:
        return abort(500, description=str(e))

if __name__ == '__main__':
    app.run(debug=True)