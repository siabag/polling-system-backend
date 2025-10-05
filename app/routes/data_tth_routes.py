# app/routes/data_tth_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.data_tth_model import DataTTH
from app.extensions import db
from werkzeug.exceptions import NotFound, Forbidden
from datetime import datetime

# Crear Blueprint para las rutas de DataTTH
data_tth_bp = Blueprint('data_tth', __name__)

# Endpoint para crear un nuevo registro de DataTTH
@data_tth_bp.route('/api/data_tth', methods=['POST'])
@jwt_required()
def create_data_tth():
    try:
        # Obtener los datos del cuerpo de la solicitud
        data = request.get_json()

        # Validar que se proporcionen los datos necesarios
        required_fields = ['device_id', 'received_at']
        if not all(field in data for field in required_fields):
            return jsonify({
                "error": True,
                "message": "Faltan datos requeridos"
            }), 400

        # Crear un nuevo registro de DataTTH
        new_data_tth = DataTTH(
            device_id=data['device_id'],
            received_at=datetime.fromisoformat(data['received_at']),
            ADC_CH0V=data.get('ADC_CH0V'),
            BatV=data.get('BatV'),
            Digital_IStatus=data.get('Digital_IStatus'),
            Door_status=data.get('Door_status'),
            EXTI_Trigger=data.get('EXTI_Trigger'),
            Work_mode=data.get('Work_mode'),
            Hum_SHT=data.get('Hum_SHT'),
            TempC_SHT=data.get('TempC_SHT'),
            TempC1=data.get('TempC1'),
            TempC_DS18B20=data.get('TempC_DS18B20'),
            Bat=data.get('Bat'),
            Interrupt_flag=data.get('Interrupt_flag'),
            Sensor_flag=data.get('Sensor_flag'),
            conduct_SOIL=data.get('conduct_SOIL'),
            temp_SOIL=data.get('temp_SOIL'),
            water_SOIL=data.get('water_SOIL')
        )

        # Guardar el registro en la base de datos
        db.session.add(new_data_tth)
        db.session.commit()

        # Devolver la respuesta con los detalles del registro creado
        return jsonify({
            "success": True,
            "data": new_data_tth.to_dict(),
            "message": "Registro de DataTTH creado exitosamente"
        }), 201

    except Exception as e:
        # Manejar errores inesperados
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al crear el registro de DataTTH: {str(e)}"
        }), 500


# Endpoint para obtener todos los registros de DataTTH
@data_tth_bp.route('/api/data_tth', methods=['GET'])
@jwt_required()
def get_all_data_tth():
    try:
        # Obtener parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('limit', 10, type=int)

        # Consultar todos los registros con paginación
        query = DataTTH.query
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        result = [
            data_tth.to_dict() for data_tth in pagination.items
        ]

        return jsonify({
            "success": True,
            "data": result,
            "total": pagination.total,
            "page": page,
            "totalPages": pagination.pages,
            "message": "Registros de DataTTH obtenidos exitosamente"
        }), 200

    except Exception as e:
        return jsonify({
            "error": True,
            "message": f"Error al obtener los registros de DataTTH: {str(e)}"
        }), 500


# Endpoint para obtener un registro específico de DataTTH por ID
@data_tth_bp.route('/api/data_tth/<int:data_tth_id>', methods=['GET'])
@jwt_required()
def get_data_tth(data_tth_id):
    try:
        # Buscar el registro por ID
        data_tth = DataTTH.query.get(data_tth_id)
        if not data_tth:
            raise NotFound("Registro de DataTTH no encontrado")

        # Devolver los detalles del registro
        return jsonify({
            "success": True,
            "data": data_tth.to_dict(),
            "message": "Registro de DataTTH obtenido exitosamente"
        }), 200

    except NotFound as e:
        return jsonify({
            "error": True,
            "message": str(e)
        }), 404

    except Exception as e:
        return jsonify({
            "error": True,
            "message": f"Error al obtener el registro de DataTTH: {str(e)}"
        }), 500


# Endpoint para actualizar un registro de DataTTH
@data_tth_bp.route('/api/data_tth/<int:data_tth_id>', methods=['PUT'])
@jwt_required()
def update_data_tth(data_tth_id):
    try:
        # Buscar el registro por ID
        data_tth = DataTTH.query.get(data_tth_id)
        if not data_tth:
            raise NotFound("Registro de DataTTH no encontrado")

        # Obtener los datos del cuerpo de la solicitud
        data = request.get_json()

        # Actualizar campos
        data_tth.device_id = data.get('device_id', data_tth.device_id)
        data_tth.received_at = datetime.fromisoformat(data['received_at']) if 'received_at' in data else data_tth.received_at
        data_tth.ADC_CH0V = data.get('ADC_CH0V', data_tth.ADC_CH0V)
        data_tth.BatV = data.get('BatV', data_tth.BatV)
        data_tth.Digital_IStatus = data.get('Digital_IStatus', data_tth.Digital_IStatus)
        data_tth.Door_status = data.get('Door_status', data_tth.Door_status)
        data_tth.EXTI_Trigger = data.get('EXTI_Trigger', data_tth.EXTI_Trigger)
        data_tth.Work_mode = data.get('Work_mode', data_tth.Work_mode)
        data_tth.Hum_SHT = data.get('Hum_SHT', data_tth.Hum_SHT)
        data_tth.TempC_SHT = data.get('TempC_SHT', data_tth.TempC_SHT)
        data_tth.TempC1 = data.get('TempC1', data_tth.TempC1)
        data_tth.TempC_DS18B20 = data.get('TempC_DS18B20', data_tth.TempC_DS18B20)
        data_tth.Bat = data.get('Bat', data_tth.Bat)
        data_tth.Interrupt_flag = data.get('Interrupt_flag', data_tth.Interrupt_flag)
        data_tth.Sensor_flag = data.get('Sensor_flag', data_tth.Sensor_flag)
        data_tth.conduct_SOIL = data.get('conduct_SOIL', data_tth.conduct_SOIL)
        data_tth.temp_SOIL = data.get('temp_SOIL', data_tth.temp_SOIL)
        data_tth.water_SOIL = data.get('water_SOIL', data_tth.water_SOIL)

        # Guardar cambios
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Registro de DataTTH actualizado exitosamente"
        }), 200

    except NotFound as e:
        return jsonify({
            "error": True,
            "message": str(e)
        }), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al actualizar el registro de DataTTH: {str(e)}"
        }), 500


# Endpoint para eliminar un registro de DataTTH
@data_tth_bp.route('/api/data_tth/<int:data_tth_id>', methods=['DELETE'])
@jwt_required()
def delete_data_tth(data_tth_id):
    try:
        # Buscar el registro por ID
        data_tth = DataTTH.query.get(data_tth_id)
        if not data_tth:
            raise NotFound("Registro de DataTTH no encontrado")

        # Eliminar el registro
        db.session.delete(data_tth)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Registro de DataTTH eliminado exitosamente"
        }), 200

    except NotFound as e:
        return jsonify({
            "error": True,
            "message": str(e)
        }), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al eliminar el registro de DataTTH: {str(e)}"
        }), 500