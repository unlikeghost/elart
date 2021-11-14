from enum import unique
from sqlalchemy.orm import defaultload
from app import db

class Usuario(db.Model):

    __tablename__ = 'usuario'

    id = db.Column(db.String(32), primary_key = True)

    usuario = db.Column(db.String(10), unique = True, nullable = False)

    password = db.Column(db.String(16), nullable = False)

    admin = db.Column(db.Boolean, nullable = False, default = False)

    def __repr__(self):

        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))

    
    def is_authenticated(self):
        
        return True

    def is_active(self):
        
        return True

    def get_id(self):

        return str(self.id)
    
    def is_anonymous(self):
        
        return False

    def get_id(self):
        
        return str(self.id)

    def is_admin(self):
        
        return self.admin

class Admin(db.Model):

    __tablename__ = 'admin'

    id = db.Column(db.String(32), primary_key = True)

    id_usuario = db.Column(db.String(32), db.ForeignKey('usuario.id'), nullable = False)

    nombre = db.Column(db.String(80), unique = True, nullable = False)

    email = db.Column(db.String(120), unique = True, nullable = False)
                
    def __repr__(self):

        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))

class Departamento(db.Model):

    __tablename__ = 'departamento'

    id = db.Column(db.String(32), primary_key = True)

    nombre = db.Column(db.String(32), nullable = False, unique = True)
    
    descripcion = db.Column(db.String(120), nullable = False)

    def __repr__(self):

        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))

class Empleado(db.Model):

    __tablename__ = 'empleado'

    id = db.Column(db.String(32), primary_key = True)

    id_usuario = db.Column(db.String(32), db.ForeignKey('usuario.id'), nullable = False)

    nombre = db.Column(db.String(80), unique = True, nullable = False)

    departamento = db.Column(db.String(80), nullable = False)

    email = db.Column(db.String(120), unique = True, nullable = False)

    def __repr__(self):

        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))

class Comentarios(db.Model):

    __tablename__ = 'comentarios'

    id = db.Column(db.String(32), primary_key = True)

    id_evaluador = db.Column(db.String(32), db.ForeignKey('empleado.id'), nullable = False)

    id_evaluado = db.Column(db.String(32), db.ForeignKey('empleado.id'), nullable = False)

    tipo = db.Column(db.Boolean, nullable = False)

    comentario = db.Column(db.String(120), nullable = False)

    def __repr__(self):

        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))

class Evaluacion(db.Model):

    __tablename__ = 'evaluaciones'

    id = db.Column(db.String(32), primary_key = True)

    id_empleado = db.Column(db.String(32), db.ForeignKey('empleado.id'), nullable = False)

    estrellas_empleado = db.Column(db.Integer, nullable = False)

    estrellas_departameto = db.Column(db.Integer, nullable = False)

    comentarios_buenos = db.Column(db.Integer, nullable = False)

    comentarios_malos = db.Column(db.Integer, nullable = False)

    def __repr__(self):

        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))