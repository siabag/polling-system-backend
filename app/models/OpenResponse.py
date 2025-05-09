from app.extensions import db

class OpenResponse(db.Model):
    __tablename__ = 'respuesta_abierta'

    id = db.Column(db.Integer, primary_key=True)
    encuesta_id = db.Column(db.Integer, db.ForeignKey('encuesta.id'), nullable=False)
    factor_id = db.Column(db.Integer, db.ForeignKey('factor.id'), nullable=False)
    respuesta_texto = db.Column(db.Text, nullable=False)
    fecha_registro = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Restricción de unicidad
    __table_args__ = (
        db.UniqueConstraint('encuesta_id', 'factor_id', name='uk_respuesta_abierta_encuesta_factor'),
    )

    # Relaciones
    encuesta = db.relationship('Survey', back_populates='respuestas_abiertas')
    factor = db.relationship('Factor', back_populates='respuestas_abiertas')

    def to_dict(self):
        return {
            "id": self.id,
            "encuesta_id": self.encuesta_id,
            "factor_id": self.factor_id,
            "respuesta_texto": self.respuesta_texto,
            "fecha_registro": self.fecha_registro
        }