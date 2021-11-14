import uuid
import hashlib
from app import db
from app import mail
from app import models
from app import executor
from . import public_bp
from flask import flash
from flask import request
from flask import url_for
from flask import redirect
from app import login_manager
from flask_mail import Message
from flask import render_template
from flask_login import login_user

@public_bp.route('/', methods=['GET'])
def index():
    """
    Main page of the website
    """

    return render_template('index.html', titulo="index")

@public_bp.route('/registro', methods=['GET'])
def registro():

    return render_template('registro.html', titulo="registro")

@public_bp.post("/api/v1/login")
def login():

    usuario = request.form['usuario']
    password = request.form['password']

    if usuario and password:

        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        usuario = models.Usuario.query.filter_by(usuario = usuario,
                                                password = hashed_password).first()

        print(usuario)                                        

        if usuario:

            print(usuario.admin)

            if usuario.admin:

                login_user(usuario)

                return redirect(url_for('admin.home'), code = 302)
            
            else:

                login_user(usuario)

                return redirect(url_for('equipo.home'), code = 302)

        else:

            flash("Usuario o contraseña incorrectos", "error")

            return redirect(url_for('public.index'), code = 302)
    
    else:

        flash("Usuario o contraseña incorrectos", "error")

        return redirect(url_for('public.index'), code = 302)

@public_bp.post("/api/v1/registroadmin")
def registroadmin():

    email = request.form['email']
    nombre = request.form['nombre']
    password = request.form['password']

    usuario = "Elart-Admin"

    if email and usuario and password and nombre:

        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        
        user = models.Usuario(id = uuid.uuid4().hex,
                              usuario = usuario,
                              password = hashed_password,
                              admin = True)
        
        try:

            db.session.add(user)

            user_data = models.Usuario.query.filter_by(usuario = usuario,
                                                       admin = True).first()

            admin = models.Admin(id = uuid.uuid4().hex,
                                 id_usuario = user_data.id,
                                 email = email,
                                 nombre = nombre)
            
            db.session.add(admin)

            db.session.commit()

            future = executor.submit(enviar_correo, email, nombre, usuario, password)
            
            if future.result():

                flash("Registro exitoso", "success")

                return redirect(url_for('public.index'), code = 302)
            
            else:

                flash("Error al enviar correo", "error")

                return redirect(url_for('public.index'), code = 302)

        except:

            flash("Ya fue registrado un administrador", "error")

            return redirect(url_for('public.index'), code = 302)

    else:

        flash("Favor de copletar los datos", "error")

        return redirect(url_for('public.registro'), code = 302)

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

@public_bp.before_app_first_request
def cargar():

    db.create_all()
    db.session.commit()

@login_manager.user_loader
def load_user(user_id):

    return models.Usuario.query.get(str(user_id))

