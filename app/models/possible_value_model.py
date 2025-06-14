from app.extensions import db

class PossibleValue(db.Model):
    __tablename__ = 'valor_posible'

    id = db.Column(db.Integer, primary_key=True)
    factor_id = db.Column(db.Integer, db.ForeignKey('factor.id'), nullable=False)
    valor = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.String(255))
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relaciones
    factor = db.relationship('Factor', back_populates='valores_posibles', lazy=True)
    respuestas = db.relationship('ResponseFactor', back_populates='valor_posible', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "factor_id": self.factor_id,
            "valor": self.valor,
            "codigo": self.codigo,
            "descripcion": self.descripcion,
            "activo": self.activo,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }