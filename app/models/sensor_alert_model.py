from app.extensions import db

class SensorAlert(db.Model):
    __tablename__ = 'sensor_alerts'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String(100), db.ForeignKey('devices.device_id'), nullable=False)
    alert_type = db.Column(db.Enum(
        'low_battery', 'high_temperature', 'low_temperature',
        'high_humidity', 'low_humidity', 'soil_dry', 'soil_wet',
        'sensor_offline', 'door_open', 'custom'
    ), nullable=False)
    alert_level = db.Column(db.Enum('info', 'warning', 'critical'), default='warning', nullable=False)
    message = db.Column(db.Text, nullable=False)
    sensor_value = db.Column(db.DECIMAL(10, 4), nullable=True)
    threshold_value = db.Column(db.DECIMAL(10, 4), nullable=True)
    is_resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.TIMESTAMP, nullable=True)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

    # Relaciones
    device = db.relationship('Device', backref=db.backref('alerts', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "alert_type": self.alert_type,
            "alert_level": self.alert_level,
            "message": self.message,
            "sensor_value": float(self.sensor_value) if self.sensor_value else None,
            "threshold_value": float(self.threshold_value) if self.threshold_value else None,
            "is_resolved": self.is_resolved,
            "resolved_at": self.resolved_at,
            "created_at": self.created_at
        }