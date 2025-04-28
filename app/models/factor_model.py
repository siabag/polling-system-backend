from app.extensions import db

class Factor(db.Model):
    __tablename__ = 'factor'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255))
    categoria = db.Column(db.String(50))
    activo = db.Column(db.Boolean, default=True)
    tipo_encuesta_id = db.Column(db.Integer, db.ForeignKey('tipo_encuesta.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relaciones
    tipo_encuesta = db.relationship('SurveyType', back_populates='factores')
    valores_posibles = db.relationship('PossibleValue', back_populates='factor', lazy=True)
    respuestas = db.relationship('ResponseFactor', back_populates='factor', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "categoria": self.categoria,
            "activo": self.activo,
            "tipo_encuesta_id": self.tipo_encuesta_id
        }