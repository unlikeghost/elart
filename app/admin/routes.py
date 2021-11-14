import uuid
import string
import random
import hashlib
import statistics

from sqlalchemy.orm import relationship
from app import db
from app import mail
from app import models
from app import executor
from . import admin_bp
from flask import flash
from flask import url_for
from flask import request
from flask import redirect
from flask_mail import Message
from flask import render_template
from flask_login import logout_user
from flask_login import current_user
from flask_login import login_required

from app import admin


TIPOS = {   0 : "thumb_down",
            1 : "thumb_up",
        }


@admin_bp.route('/auth/admin/home', methods=['GET'])
@login_required
def home():

    curren_id = current_user.id

    current_user_data = models.Admin.query.filter_by(id_usuario = curren_id).first()

    current_name = current_user_data.nombre.capitalize()

    current_data  = models.Evaluacion.query.filter_by().all()

    if current_data:

        data_comentarios = models.Comentarios.query.filter_by().limit(4).all()

        comentarios = [comentario.comentario.capitalize() for comentario in data_comentarios]

        tiposComentarios = [comentario.tipo for comentario in data_comentarios]

        estrellas_departamentos = [evaluacion.estrellas_departameto for evaluacion in current_data]

        promedio_estrellas_departamento = int(statistics.mean(estrellas_departamentos))

        estrellas_empleados = [evaluacion.estrellas_empleado for evaluacion in current_data]

        promedio_estrellas_empleados = int(statistics.mean(estrellas_empleados))

        comentarios_buenos = len([evaluacion.comentarios_buenos for evaluacion in current_data if evaluacion.comentarios_buenos])

        porcentaje_comentarios_buenos = (comentarios_buenos * 100) / len(current_data)

        print(porcentaje_comentarios_buenos)
        comentarios_malos = len([evaluacion.comentarios_malos for evaluacion in current_data if evaluacion.comentarios_malos])

        porcentaje_comentarios_malos = (comentarios_malos * 100) / len(current_data)

        valueschart = [porcentaje_comentarios_buenos, porcentaje_comentarios_malos]

        labelschart = ['Buenos', 'Malos']

        tipos = [TIPOS[comentarios.tipo] for comentarios in data_comentarios]

        colors = ['rgb(0, 187, 45)', 'rgb(173, 0, 15)']

        return render_template('admin/home.html',
                                titulo = 'Home',
                                marcador = True,
                                nombre = current_name,
                                tipo = 'Admin',
                                estrellasdepartamento = promedio_estrellas_departamento,
                                estrellasempleados = promedio_estrellas_empleados,
                                charttitle = "Comentarios",
                                labels = labelschart,
                                colors = colors,
                                values = valueschart,
                                tipoComentario = tipos,
                                comentarios = comentarios,)

    else:
    
        return render_template('admin/home.html',
                                titulo='Home',
                                marcador = False,
                                nombre = current_name,
                                tipo = "Admin")

@admin_bp.route('/auth/admin/departamentos', methods=['GET'])
@login_required
def departamentos():

    curren_id = current_user.id

    current_user_data = models.Admin.query.filter_by(id_usuario = curren_id).first()

    current_name = current_user_data.nombre

    current_data = models.Departamento.query.all()

    if current_data:

        departamentos = [departamento.nombre for departamento in current_data]

        return render_template('admin/departamento.html',
                                titulo = 'Departamentos',
                                marcador = True,
                                nombre = current_name,
                                departamentos = departamentos
                                )

    else:

        return render_template('admin/departamento.html',
                                titulo = 'Departamentos',
                                marcador = False,
                                nombre = current_name,
                                )

@admin_bp.route('/auth/admin/usuario', methods=['GET',])
@login_required
def usuarios():

    curren_id = current_user.id

    current_user_data = models.Admin.query.filter_by(id_usuario = curren_id).first()

    current_name = current_user_data.nombre

    current_data_empleado  = models.Empleado.query.all()

    curren_data_departamentos = models.Departamento.query.all()

    if current_data_empleado and  curren_data_departamentos:

        departamentos = [departamento.nombre for departamento in curren_data_departamentos]

        empleados = [empleado.nombre for empleado in current_data_empleado]

        return render_template('admin/usuario.html',
                                titulo = 'Usuarios',
                                marcador = True,
                                nombre = current_name,
                                departamentos = departamentos,
                                nombres = empleados,
                                )

    elif curren_data_departamentos:

        departamentos = [departamento.nombre for departamento in curren_data_departamentos]

        return render_template('admin/usuario.html',
                                titulo = 'Usuarios',
                                marcador = False,
                                nombre = current_name,
                                departamentos = departamentos,
                                )
    
    elif not(curren_data_departamentos) and not(curren_data_departamentos):

        flash('No hay departamentos registrados aun', "warning")\
        
        return redirect(url_for('admin.home'))

@admin_bp.route('/auth/admin/reportes', methods=['GET', 'POST'])
@login_required
def reportes():
    
    curren_id = current_user.id

    current_user_data = models.Admin.query.filter_by(id_usuario = curren_id).first()

    current_name = current_user_data.nombre

    current_data = models.Departamento.query.all()

    if request.method == 'POST':

        departamento = request.form['departamento']

        usuarios_data = models.Empleado.query.filter_by(departamento=departamento).all()

        if len(usuarios_data):

            nombres = [usuario.nombre for usuario in usuarios_data]

            ids_empleados = [usuario.id for usuario in usuarios_data]

            evaluaciones_data = models.Evaluacion.query.filter(models.Evaluacion.id_empleado.in_(ids_empleados)).all()

            if evaluaciones_data:

                estrellas = [evaluacion.estrellas_empleado for evaluacion in evaluaciones_data]

                return render_template('admin/reporte.html',
                                        titulo = 'Reportes',
                                        marcador = True,
                                        nombre = current_name,
                                        miembro = nombres,
                                        departamentos = departamento,
                                        estrellas = estrellas,
                                        )
            else:

                flash('No hay evaluaciones registradas aun', "warning")
                
                return redirect(url_for('admin.reportes'))
            
        else:

            flash('No hay usuarios registrados en el departamento seleccionado', "warning")

            return redirect(url_for('admin.reportes'))

    else:

        if current_data:

            departamentos = [departamento.nombre for departamento in current_data]

            return render_template('admin/reporte.html',
                                    titulo = 'Reportes',
                                    marcador = False,
                                    nombre = current_name,
                                    departamentos = departamentos
                                    )

        else:

            flash('No hay departamentos registrados aun', "warning")

            return redirect(url_for('admin.home'))

@admin_bp.route('/auth/admin/editar/<nombre>/<correo>', methods=['GET'])
@login_required
def editar_usuario(nombre = None, correo = None):

    if nombre and correo:

        curren_data = models.Departamento.query.all()

        departamentos = [departamento.nombre for departamento in curren_data]

        return render_template('admin/editar.html',
                                nombre = nombre,
                                correo = correo,
                                departamentos = departamentos,
                                )
    else:

        return redirect(url_for('admin.home'))

@admin_bp.route("/auth/admin/logout",  methods=['GET'])
@login_required
def logout():

    logout_user()

    return redirect(url_for('public.index'))

@admin_bp.post('/api/v1/admin/administrar/usuario')
@login_required
def administrar_usuario():

    if request.form["action"] == "eliminar":

        nombre = request.form["nombre"]

        departamento = request.form["departamento"]

        if nombre and departamento:

            usuarios_data = models.Empleado.query.filter_by(nombre = nombre,
                                                            departamento = departamento).first()

            id_usuario =  usuarios_data.id_usuario                                              

            models.Usuario.query.filter_by(id = id_usuario).delete()
            models.Empleado.query.filter_by(id_empleado = id_usuario).delete()

            db.session.commit()

            flash('Usuario eliminado correctamente', "success")

            return redirect(url_for('admin.home'), 302)

        else:

            flash('No se ha seleccionado ningun usuario', "warning")

            return redirect(url_for('admin.usuarios'))

    elif request.form["action"] == "editar":

        nombre = request.form["nombre"]

        departamento = request.form["departamento"]

        usuarios_data = models.Empleado.query.filter_by(nombre = nombre,
                                                        departamento = departamento).first()
        
        correo = usuarios_data.correo
        nombre = usuarios_data.nombre



        return render_template('admin/editar.html',
                                nombre = nombre,
                                correo = correo,
                                )

@admin_bp.post('/api/v1/admin/editar/usuario')
@login_required
def apieditar_usuario():

    nombre = request.form["nombre"]
    correo = request.form["email"]
    departamento = request.form["departamento"]

    if correo and nombre and departamento:

        usuarios_data = models.Empleado.query.filter_by(nombre = nombre,
                                                        departamento = departamento,
                                                        email = correo).first()

        usuarios_data.departamento = departamento

        usuarios_data.email = correo

        usuarios_data.nombre = nombre                                                        

        db.session.commit()

        flash('Usuario editado correctamente', "success")

        return redirect(url_for('admin.home'), 302)

    else:

        flash('Porfavor rellene todos los espacios', "warning")

        return redirect(url_for('admin.editar_usuario', nombre = nombre, correo = correo), 302)

@admin_bp.post("/api/v1/admin/crear/departamento")
@login_required
def crear_departamento():

    nombre = request.form["departamento"]
    descripcion = request.form["descripcion"]

    if nombre and descripcion:

        departamento = models.Departamento(nombre = nombre,
                                           descripcion = descripcion,
                                           id = uuid.uuid4().hex)

        try:

            db.session.add(departamento)
            db.session.commit()

            flash("Departamento creado con éxito", "success")
            return redirect(url_for('admin.home'), 302)
        
        except:

            flash("Error al crear el departamento", "error")
            return redirect(url_for('admin.departamentos'), 302)

    else:

        flash ("Llene todos los datos", "warning")
        return redirect(url_for('admin.departamentos'), 302)

@admin_bp.post("/api/v1/admin/crear/usuario")
@login_required
def crear_usuario():
    
    nombre = request.form['nombre']
    departamento = request.form['departamento']
    correo = request.form['email']

    if correo and departamento and nombre:

        caracteres = string.ascii_letters + string.digits

        usuario = "team-" + "".join(random.choice(caracteres) for _ in range(5))

        password = "".join(random.choice(caracteres) for _ in range(8))

        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        user = models.Usuario(id = uuid.uuid4().hex,
                               usuario = usuario,
                               password = hashed_password,
                               admin = False)

        try:

            db.session.add(user)
            db.session.commit()

        except:

            flash("Nombre de usuario o correo ya registrados", "error")
            return redirect(url_for('admin.usuarios'), 302)   

        data = models.Usuario.query.filter_by(usuario = usuario, admin = False).first()

        empleado = models.Empleado(id = uuid.uuid4().hex,
                                   nombre = nombre,
                                   id_usuario = data.id,
                                   departamento = departamento,
                                   email = correo)

        try:

            db.session.add(empleado)
            db.session.commit()

            future = executor.submit(enviar_correo, correo, nombre, usuario, password)

            if future.result():

                flash("Usuario creado con éxito", "success")
                return redirect(url_for('admin.home'), 302)
            
            else:

                flash("Error al enviar el correo, porfavor intetne de nuevo", "error")
                return redirect(url_for('admin.usuarios'), 302)

        except:

            flash("Nombre de usuario o correo ya registrados", "error")
            return redirect(url_for('admin.usuarios'), 302)   

    else:

        flash("Llene todos los datos", "warning")
        return redirect(url_for('admin.usuarios'), 302)

@admin_bp.post("/api/v1/admin/eliminar/departamento")
@login_required
def eliminar_departamento():

    departamento = request.form['departamento']

    if departamento:

        departamento = models.Departamento.query.filter_by(nombre = departamento).first()

        usuarios = models.Empleado.query.filter_by(departamento = departamento.nombre).all()

        if usuarios:

            for usuario in usuarios:

                models.Usuario.query.filter_by(id = usuario.id_usuario).delete()
                models.Empleado.query.filter_by(usuario_id = usuario.id_usuario).delete()

            db.session.commit()
        
        models.Departamento.query.filter_by(nombre = departamento.nombre).delete()
        
        db.session.commit()

        flash("Departamento eliminado con éxito", "success")
        return redirect(url_for('admin.home'), 302)

    else:

        flash("Seleccione todos los datos pedidos", "warning")

        return redirect(url_for('admin.departamentos'), 302)


def enviar_correo(email: str, nombre: str, usuario: str, password: str):
    
    msg = Message("Ah sido registrado en E-lart",
                  sender = "elart.mexico@gmail.com",
                  recipients = [email])
        
    msg.body = f"Hola, {nombre}!\n\nTu usuario es: {usuario} \nTu contraseña es: {password}\n\nGracias por registrarte en E-lart"

    try:

        mail.send(msg)
        
        return True

    except:

        return False
