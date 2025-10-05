from app.extensions import db

class AlertThreshold(db.Model):
    __tablename__ = 'alert_thresholds'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String(100), db.ForeignKey('devices.device_id'), nullable=False)
    sensor_field = db.Column(db.String(50), nullable=False)
    threshold_type = db.Column(db.Enum('min', 'max'), nullable=False)
    threshold_value = db.Column(db.DECIMAL(10, 4), nullable=False)
    alert_level = db.Column(db.Enum('info', 'warning', 'critical'), default='warning', nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relaciones
    device = db.relationship('Device', backref=db.backref('alert_thresholds', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "sensor_field": self.sensor_field,
            "threshold_type": self.threshold_type,
            "threshold_value": float(self.threshold_value),
            "alert_level": self.alert_level,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }