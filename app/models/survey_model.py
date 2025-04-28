from app.extensions import db

class Survey(db.Model):
    __tablename__ = 'encuesta'

    id = db.Column(db.Integer, primary_key=True)
    fecha_aplicacion = db.Column(db.Date, nullable=False)
    observaciones = db.Column(db.Text)
    completada = db.Column(db.Boolean, default=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    finca_id = db.Column(db.Integer, db.ForeignKey('finca.id'), nullable=False)
    tipo_encuesta_id = db.Column(db.Integer, db.ForeignKey('tipo_encuesta.id'), nullable=False)

    # Relaciones
    usuario = db.relationship('User', back_populates='encuestas')
    finca = db.relationship('Farm', back_populates='encuestas')
    tipo_encuesta = db.relationship('SurveyType', back_populates='encuestas')
    respuestas = db.relationship('ResponseFactor', back_populates='encuesta', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "fecha_aplicacion": self.fecha_aplicacion,
            "observaciones": self.observaciones,
            "completada": self.completada,
            "usuario_id": self.usuario_id,
            "finca_id": self.finca_id,
            "tipo_encuesta_id": self.tipo_encuesta_id
        }