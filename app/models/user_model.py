from app.extensions import db

class User(db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False, unique=True)
    contrasena_hash = db.Column(db.String(255), nullable=False)
    fecha_creacion = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    activo = db.Column(db.Boolean, default=True)
    rol_id = db.Column(db.Integer, db.ForeignKey('rol.id'), nullable=False)

    # Relaciones
    rol = db.relationship('Role', back_populates='usuarios')
    fincas = db.relationship('Farm', back_populates='usuario', lazy=True)
    encuestas = db.relationship('Survey', back_populates='usuario', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "correo": self.correo,
            "activo": self.activo,
            "rol": self.rol.nombre if self.rol else None
        }