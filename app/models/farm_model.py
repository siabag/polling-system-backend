from app.extensions import db

class Farm(db.Model):
    __tablename__ = 'finca'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ubicacion = db.Column(db.String(255))
    latitud = db.Column(db.DECIMAL(10, 8))
    longitud = db.Column(db.DECIMAL(11, 8))
    propietario = db.Column(db.String(100))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relaciones
    usuario = db.relationship('User', back_populates='fincas', lazy=True)
    encuestas = db.relationship('Survey', back_populates='finca', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "ubicacion": self.ubicacion,
            "latitud": str(self.latitud),
            "longitud": str(self.longitud),
            "propietario": self.propietario,
            "usuario_id": self.usuario_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }