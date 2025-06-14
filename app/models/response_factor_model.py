from app.extensions import db

class ResponseFactor(db.Model):
    __tablename__ = 'respuesta_factor'

    id = db.Column(db.Integer, primary_key=True)
    encuesta_id = db.Column(db.Integer, db.ForeignKey('encuesta.id'), nullable=False)
    factor_id = db.Column(db.Integer, db.ForeignKey('factor.id'), nullable=False)
    valor_posible_id = db.Column(db.Integer, db.ForeignKey('valor_posible.id'), nullable=False)
    respuesta_texto = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relaciones
    encuesta = db.relationship('Survey', back_populates='respuestas', lazy=True)
    factor = db.relationship('Factor', back_populates='respuestas', lazy=True)
    valor_posible = db.relationship('PossibleValue', back_populates='respuestas', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "encuesta_id": self.encuesta_id,
            "factor_id": self.factor_id,
            "valor_posible_id": self.valor_posible_id,
            "respuesta_texto": self.respuesta_texto,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }