from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.data_tth_model import DataTTH
from datetime import datetime, date

data_tth_bp = Blueprint('data_tth', __name__)

@data_tth_bp.route('/api/data_tth', methods=['GET'])
@jwt_required()
def get_data_tth_by_date():
    try:
        # Obtener parámetros de fecha (formato esperado: YYYY-MM-DD)
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        # Si no se envían fechas, usar el rango del primer día del mes hasta hoy
        if not start_date_str or not end_date_str:
            today = date.today()
            start_date = today.replace(day=1)
            end_date = today
        else:
            # Convertir strings a objetos datetime
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        # Convertir a cadenas para comparar con received_at (que es VARCHAR)
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        # Consultar registros filtrando por rango de fechas
        query = DataTTH.query.filter(
            DataTTH.received_at.between(start_date_str, end_date_str)
        ).order_by(DataTTH.received_at.asc())

        records = query.all()

        if not records:
            return jsonify({
                "success": True,
                "data": {},
                "message": "No se encontraron registros en el rango de fechas especificado"
            }), 200

        # Crear estructura agrupada para las 4 métricas
        grouped_data = {
            "temperatura_ambiente": [],
            "humedad_ambiente": [],
            "temperatura_suelo": [],
            "humedad_suelo": []
        }

        for r in records:
            # Omitir registros sin datos válidos
            if not any([r.TempC_SHT, r.Hum_SHT, r.temp_SOIL, r.water_SOIL]):
                continue

            if r.TempC_SHT is not None:
                grouped_data["temperatura_ambiente"].append({
                    "fecha_hora": r.received_at,
                    "valor": r.TempC_SHT
                })
            if r.Hum_SHT is not None:
                grouped_data["humedad_ambiente"].append({
                    "fecha_hora": r.received_at,
                    "valor": r.Hum_SHT
                })
            if r.temp_SOIL is not None:
                grouped_data["temperatura_suelo"].append({
                    "fecha_hora": r.received_at,
                    "valor": r.temp_SOIL
                })
            if r.water_SOIL is not None:
                grouped_data["humedad_suelo"].append({
                    "fecha_hora": r.received_at,
                    "valor": r.water_SOIL
                })

        return jsonify({
            "success": True,
            "data": grouped_data,
            "total_registros": len(records),
            "rango_fechas": {
                "inicio": start_date_str,
                "fin": end_date_str
            },
            "message": "Datos obtenidos exitosamente"
        }), 200

    except Exception as e:
        return jsonify({
            "error": True,
            "message": f"Error al obtener los registros: {str(e)}"
        }), 500
