import uuid
import requests
import statistics
from app import db
from app import models
from app import executor
from . import equipo_bp
from flask import flash
from flask import url_for
from flask import request
from flask import redirect
from flask_mail import Message
from flask import render_template
from flask_login import logout_user
from flask_login import current_user
from flask_login import login_required

INSIGNIAS = {   0: "Novato",
                1: "Artisan",
                2: "Venti",
                3: "Trenta",
                4: "Artiste",
                5: "Gimont",
            }

TIPOS = {   0 : "thumb_down",
            1 : "thumb_up",
        }

CLASES  = { 
            0 : False,
            1 : True,}

@equipo_bp.route('/auth/equipo/home', methods=['GET'])
@login_required
def home():

    curren_id = current_user.id

    current_user_data = models.Empleado.query.filter_by(id_usuario = curren_id).first()

    current_name = current_user_data.nombre

    current_id_empleado = current_user_data.id

    current_departament = current_user_data.departamento

    current_data_evaluaciones = models.Evaluacion.query.filter_by(id_empleado = current_id_empleado).limit(2).all()

    current_departament_user = models.Empleado.query.filter_by(departamento = current_departament).all()

    current_data_commentarios = models.Comentarios.query.filter_by(id_evaluado = current_id_empleado).limit(2).all()

    if current_data_evaluaciones:

        puntos = len(current_data_evaluaciones)

        comentarios = [comentario.comentario for comentario in current_data_commentarios]

        comentario_buenos = [comentario.tipo for comentario in current_data_commentarios if comentario.tipo == 1]

        comentarios_malos = [comentario.tipo for comentario in current_data_commentarios if comentario.tipo == 0]

        total_comentarios = len(comentarios)

        tipos = [TIPOS[comentarios.tipo] for comentarios in current_data_commentarios]

        estrellas = [current_data_evaluaciones.estrellas_empleado for current_data_evaluaciones in current_data_evaluaciones]

        promedio_estrellas = int(statistics.mean(estrellas))
        
        porcentaje_comentarios_buenos = (len(comentario_buenos) * 100) / total_comentarios

        porcentaje_comentarios_malos = (len(comentarios_malos) * 100) / total_comentarios

        values = [porcentaje_comentarios_buenos, porcentaje_comentarios_malos]

        labels = ["Buenos", "Malos"]

        miembrosx = [miembros.nombre for miembros in current_departament_user]

        colors = ['rgb(0, 187, 45)', 'rgb(173, 0, 15)']

        print(tipos)
        print(comentarios)
        # print(current_departament_user.nombre)

        return render_template('equipo/home.html',
                                nombre = current_name,
                                titulo = "Home",
                                departamento = current_departament,
                                insignia = INSIGNIAS[promedio_estrellas],
                                promedioEstrellas = promedio_estrellas,
                                marcador = True,
                                puntos = puntos,
                                tipoComentario = tipos,
                                comentarios = comentarios,
                                labels = labels,
                                colors = colors,
                                values = values,
                                miembros = miembrosx,
                                )
    
    else:

        miembros = [miembros.nombre for miembros in current_departament_user]
        
        return render_template('equipo/home.html',
                                nombre = current_name,
                                titulo = "Home",
                                departamento = current_departament,
                                insignia = INSIGNIAS[0],
                                promedioEstrellas = 0,
                                marcador = False,
                                nombres = miembros)

@equipo_bp.route("/auth/equipo/evaluacion", methods=["GET", "POST"])
@login_required
def evaluacion():

    current_id = current_user.id

    current_user_data = models.Empleado.query.filter_by(id_usuario = current_id).first()

    nombre = current_user_data.nombre

    departament_data = models.Departamento.query.filter_by().all()

    usuarios = models.Empleado.query.filter( models.Empleado.id_usuario != current_id).all()

    if departament_data:

        departamentos = [departamento.nombre for departamento in departament_data]

        nombres = [usuario.nombre for usuario in usuarios]

        return render_template('equipo/evaluacion.html',
                                nombre = nombre,
                                departamentos = departamentos,
                                nombres = nombres,
                                )

    else:

        flash("No hay departamentos registrados aun", "info")
        return redirect(url_for("equipo.index"))

@equipo_bp.route("/auth/equipo/logout",  methods=['GET'])
@login_required
def logout():

    logout_user()

    return redirect(url_for('public.index'))

@equipo_bp.post("/api/v1/equipo/evaluacion")
@login_required
def evaluacion_api():

    departamnento = request.form["departamento"]
    empleado = request.form["nombre"]
    estrellas_dep = request.form["rate--dep"]
    estellas_emp = request.form["rate--empleado"]
    comentarios = request.form["comentario"]

    if departamnento and empleado and estrellas_dep and estellas_emp and comentarios:

        future = executor.submit(predict, comentarios)

        response = future.result()

        clasifiacion = int(response["pred"])

        clasifiacion = CLASES[clasifiacion]

        estrella_dep = int(estrellas_dep)

        estrella_emp = int(estellas_emp)

        data_evaluado = models.Empleado.query.filter_by(nombre = empleado).first()

        data_evaluador = models.Empleado.query.filter_by(id_usuario = current_user.id).first()

        coments = models.Comentarios(id = uuid.uuid4().hex,
                                     id_evaluador = data_evaluador.id,
                                     id_evaluado = data_evaluado.id,
                                     tipo = clasifiacion,
                                     comentario = comentarios)
        
        if clasifiacion:
            eval = models.Evaluacion(id = uuid.uuid4().hex,
                                    id_empleado = data_evaluado.id,
                                    estrellas_empleado =  estrella_emp,
                                    estrellas_departameto = estrella_dep,
                                    comentarios_buenos = 1,
                                    comentarios_malos = 0,)
        
        else:

            eval = models.Evaluacion(id = uuid.uuid4().hex,
                                    id_empleado = data_evaluado.id,
                                    estrellas_empleado =  estrella_emp,
                                    estrellas_departameto = estrella_dep,
                                    comentarios_buenos = 0,
                                    comentarios_malos = 1,)
            
        db.session.add(eval)
        db.session.commit()
        
        db.session.add(coments)
        db.session.commit()

        flash("Evaluacion enviada", "success")
        return redirect(url_for("equipo.home"))

    else:
            
        flash("Debes llenar todos los campos", "warning")
        return redirect(url_for("equipo.evaluacion")) 
        
def predict(comentario: str) -> dict:

    url = "https://pruebaapi-332010.nn.r.appspot.com/modelo"
    payload = {'comentarios': comentario}

    response = requests.post(url, json=payload)

    return response.json()