from app.extensions import db

class Survey(db.Model):
    __tablename__ = 'encuesta'

    id = db.Column(db.Integer, primary_key=True)
    fecha_aplicacion = db.Column(db.Date, nullable=False)
    tipo_encuesta_id = db.Column(db.Integer, db.ForeignKey('tipo_encuesta.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    finca_id = db.Column(db.Integer, db.ForeignKey('finca.id'), nullable=False)
    observaciones = db.Column(db.Text)
    completada = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relaciones
    tipo_encuesta = db.relationship('SurveyType', back_populates='encuestas', lazy=True)
    usuario = db.relationship('User', back_populates='encuestas', lazy=True)
    finca = db.relationship('Farm', back_populates='encuestas', lazy=True)
    respuestas = db.relationship('ResponseFactor', back_populates='encuesta', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "fecha_aplicacion": self.fecha_aplicacion,
            "tipo_encuesta_id": self.tipo_encuesta_id,
            "usuario_id": self.usuario_id,
            "finca_id": self.finca_id,
            "observaciones": self.observaciones,
            "completada": self.completada,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }