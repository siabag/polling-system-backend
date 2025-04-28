from app.extensions import db

class Role(db.Model):
    __tablename__ = 'rol'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)

    # Relación con usuarios
    usuarios = db.relationship('User', back_populates='rol', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre
        }