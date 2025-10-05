from app.extensions import db

class Device(db.Model):
    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String(100), nullable=False, unique=True)
    device_name = db.Column(db.String(255), nullable=True)
    device_type = db.Column(db.String(100), nullable=True)
    location_name = db.Column(db.String(255), nullable=True)
    latitude = db.Column(db.DECIMAL(10, 8), nullable=True)
    longitude = db.Column(db.DECIMAL(11, 8), nullable=True)
    installation_date = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relaciones
    alert_thresholds = db.relationship('AlertThreshold', backref=db.backref('device', lazy=True))
    alerts = db.relationship('SensorAlert', backref=db.backref('device', lazy=True))
    data_tth_entries = db.relationship('DataTTH', backref=db.backref('device', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "device_name": self.device_name,
            "device_type": self.device_type,
            "location_name": self.location_name,
            "latitude": float(self.latitude) if self.latitude else None,
            "longitude": float(self.longitude) if self.longitude else None,
            "installation_date": self.installation_date.isoformat() if self.installation_date else None,
            "is_active": self.is_active,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }