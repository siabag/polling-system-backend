from app.extensions import db

class DataTTH(db.Model):
    __tablename__ = 'data_tth'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String(50), nullable=False)
    ADC_CH0V = db.Column(db.Float, nullable=True)
    BatV = db.Column(db.Float, nullable=True)
    Digital_IStatus = db.Column(db.String(5), nullable=True)
    Door_status = db.Column(db.String(10), nullable=True)
    EXTI_Trigger = db.Column(db.String(10), nullable=True)
    Hum_SHT = db.Column(db.Float, nullable=True)
    TempC1 = db.Column(db.Float, nullable=True)
    TempC_SHT = db.Column(db.Float, nullable=True)
    Work_mode = db.Column(db.String(10), nullable=True)
    received_at = db.Column(db.String(50), nullable=True)
    Bat = db.Column(db.String(10), nullable=True)
    Interrupt_flag = db.Column(db.Integer, nullable=True)
    Sensor_flag = db.Column(db.Integer, nullable=True)
    TempC_DS18B20 = db.Column(db.Float, nullable=True)
    conduct_SOIL = db.Column(db.Float, nullable=True)
    temp_SOIL = db.Column(db.Float, nullable=True)
    water_SOIL = db.Column(db.Float, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "ADC_CH0V": self.ADC_CH0V,
            "BatV": self.BatV,
            "Digital_IStatus": self.Digital_IStatus,
            "Door_status": self.Door_status,
            "EXTI_Trigger": self.EXTI_Trigger,
            "Hum_SHT": self.Hum_SHT,
            "TempC1": self.TempC1,
            "TempC_SHT": self.TempC_SHT,
            "Work_mode": self.Work_mode,
            "received_at": self.received_at,
            "Bat": self.Bat,
            "Interrupt_flag": self.Interrupt_flag,
            "Sensor_flag": self.Sensor_flag,
            "TempC_DS18B20": self.TempC_DS18B20,
            "conduct_SOIL": self.conduct_SOIL,
            "temp_SOIL": self.temp_SOIL,
            "water_SOIL": self.water_SOIL
        }