from app.extensions import db

class DataTTH(db.Model):
    __tablename__ = 'data_tth'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String(100), nullable=False)
    ADC_CH0V = db.Column(db.DECIMAL(8, 4), nullable=True)
    BatV = db.Column(db.DECIMAL(6, 3), nullable=True)
    Digital_IStatus = db.Column(db.String(50), nullable=True)
    Door_status = db.Column(db.String(50), nullable=True)
    EXTI_Trigger = db.Column(db.String(50), nullable=True)
    Hum_SHT = db.Column(db.DECIMAL(6, 2), nullable=True)
    TempC1 = db.Column(db.DECIMAL(6, 2), nullable=True)
    TempC_SHT = db.Column(db.DECIMAL(6, 2), nullable=True)
    Work_mode = db.Column(db.String(50), nullable=True)
    received_at = db.Column(db.TIMESTAMP, nullable=False)
    Bat = db.Column(db.Integer, nullable=True)
    Interrupt_flag = db.Column(db.Integer, nullable=True)
    Sensor_flag = db.Column(db.Integer, nullable=True)    
    TempC_DS18B20 = db.Column(db.DECIMAL(6, 2), nullable=True)
    conduct_SOIL = db.Column(db.DECIMAL(8, 2), nullable=True)
    temp_SOIL = db.Column(db.DECIMAL(6, 2), nullable=True)
    water_SOIL = db.Column(db.DECIMAL(6, 2), nullable=True)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "ADC_CH0V": float(self.ADC_CH0V) if self.ADC_CH0V else None,
            "BatV": float(self.BatV) if self.BatV else None,
            "Digital_IStatus": self.Digital_IStatus,
            "Door_status": self.Door_status,
            "EXTI_Trigger": self.EXTI_Trigger,
            "Hum_SHT": float(self.Hum_SHT) if self.Hum_SHT else None,
            "TempC1": float(self.TempC1) if self.TempC1 else None,
            "TempC_SHT": float(self.TempC_SHT) if self.TempC_SHT else None,
            "Work_mode": self.Work_mode,
            "received_at": self.received_at,
            "Bat": self.Bat,
            "Interrupt_flag": self.Interrupt_flag,
            "Sensor_flag": self.Sensor_flag,
            "TempC_DS18B20": float(self.TempC_DS18B20) if self.TempC_DS18B20 else None,
            "conduct_SOIL": float(self.conduct_SOIL) if self.conduct_SOIL else None,
            "temp_SOIL": float(self.temp_SOIL) if self.temp_SOIL else None,
            "water_SOIL": float(self.water_SOIL) if self.water_SOIL else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }