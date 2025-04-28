from app.extensions import db

class SurveyType(db.Model):
    __tablename__ = 'tipo_encuesta'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    descripcion = db.Column(db.String(255))
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relaciones
    factores = db.relationship('Factor', back_populates='tipo_encuesta', lazy=True)
    encuestas = db.relationship('Survey', back_populates='tipo_encuesta', lazy=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "activo": self.activo
        }