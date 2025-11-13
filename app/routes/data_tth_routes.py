from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required
from app.models.data_tth_model import DataTTH
from datetime import datetime, date, timedelta
from collections import defaultdict
import csv
import io
import traceback

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

        # Crear estructura agrupada para las 5 métricas
        grouped_data = {
            "temperatura_ambiente": [],
            "humedad_ambiente": [],
            "temperatura_suelo": [],
            "humedad_suelo": [],
            "conductividad_suelo": []
        }

        for r in records:
            # Omitir registros sin datos válidos
            if not any([r.TempC_SHT, r.Hum_SHT, r.temp_SOIL, r.water_SOIL, r.conduct_SOIL]):
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
            if r.conduct_SOIL is not None:
                grouped_data["conductividad_suelo"].append({
                    "fecha_hora": r.received_at,
                    "valor": r.conduct_SOIL
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

@data_tth_bp.route('/api/data_tth/csv', methods=['GET'])
@jwt_required()
def download_data_tth_csv():
    try:
        # Obtener parámetros de fecha
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        # Establecer rango por defecto si no se proporcionan fechas
        if not start_date_str or not end_date_str:
            today = date.today()
            start_date = today.replace(day=1)
            end_date = today
        else:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        # Convertir a strings en formato YYYY-MM-DD para comparación lexicográfica
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        query = DataTTH.query.filter(
            DataTTH.received_at >= start_date_str,
            DataTTH.received_at < f"{end_date_str}z"
        ).order_by(DataTTH.received_at.asc())

        records = query.all()

        if not records:
            return jsonify({
                "error": True,
                "message": "No se encontraron registros para exportar en el rango especificado."
            }), 404

        # Crear CSV en memoria
        output = io.StringIO()
        writer = csv.writer(output)

        # Encabezados: incluir conductividad del suelo
        writer.writerow([
            "received_at",
            "device_id",
            "TempC_SHT",
            "Hum_SHT",
            "temp_SOIL",
            "water_SOIL",
            "conduct_SOIL"
        ])

        # Escribir filas
        for r in records:
            writer.writerow([
                r.received_at or '',
                r.device_id or '',
                r.TempC_SHT if r.TempC_SHT is not None else '',
                r.Hum_SHT if r.Hum_SHT is not None else '',
                r.temp_SOIL if r.temp_SOIL is not None else '',
                r.water_SOIL if r.water_SOIL is not None else '',
                r.conduct_SOIL if r.conduct_SOIL is not None else ''
            ])

        output.seek(0)
        filename = f"data_tth_{start_date_str}_to_{end_date_str}.csv"

        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename={filename}'
            }
        )

    except ValueError as ve:
        return jsonify({
            "error": True,
            "message": "Formato de fecha inválido. Use YYYY-MM-DD."
        }), 400
    except Exception as e:
        return jsonify({
            "error": True,
            "message": f"Error al generar el archivo CSV: {str(e)}"
        }), 500
    
@data_tth_bp.route('/api/data_tth/monthly_summary', methods=['GET'])
@jwt_required()
def get_monthly_summary():
    try:
        # Obtener parámetros de fecha
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        # Consultar la fecha más antigua en la base de datos
        oldest_record = DataTTH.query.order_by(DataTTH.received_at.asc()).first()
        if not oldest_record:
            return jsonify({
                "success": True,
                "data": {
                    "notas": {},
                    "summary": []
                },
                "message": "No hay datos disponibles en la base de datos"
            }), 200

        # Fecha más antigua (default para start_date)
        # Parsear formato ISO 8601: YYYY-MM-DDTHH:MM:SS.fZ
        oldest_date = datetime.fromisoformat(oldest_record.received_at.replace('Z', '+00:00')).date()

        # Último día del mes anterior (default para end_date)
        today = date.today()
        first_day_of_current_month = today.replace(day=1)
        last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)

        # Asignar valores por defecto si no se proporcionan fechas
        if not start_date_str:
            start_date = oldest_date
        else:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()

        if not end_date_str:
            end_date = last_day_of_previous_month
        else:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        # Convertir a cadenas
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        # Consultar registros filtrando por rango de fechas
        query = DataTTH.query.filter(
            DataTTH.received_at.between(start_date_str, end_date_str)
        )

        records = query.all()

        if not records:
            return jsonify({
                "success": True,
                "data": {
                    "notas": {},
                    "summary": []
                },
                "message": "No se encontraron registros en el rango de fechas especificado"
            }), 200

        # Agrupar por mes
        monthly_data = defaultdict(lambda: {
            "temperatura": [],
            "humedad": [],
            "year": None,
            "month": None
        })

        for r in records:
            # Extraer fecha del campo received_at (formato ISO 8601)
            try:
                dt = datetime.fromisoformat(r.received_at.replace('Z', '+00:00'))
                year = dt.year
                month = dt.month
                month_key = f"{dt.strftime('%B')} de {year}"
            except Exception:
                continue  # Omitir registros con fechas inválidas

            if r.TempC_SHT is not None:
                monthly_data[month_key]["temperatura"].append(r.TempC_SHT)
            if r.Hum_SHT is not None:
                monthly_data[month_key]["humedad"].append(r.Hum_SHT)

            # Guardar year y month para ordenar
            monthly_data[month_key]["year"] = year
            monthly_data[month_key]["month"] = month

        # Calcular estadísticas y preparar summary
        summary = []
        for month_key, data in monthly_data.items():
            temp_vals = data["temperatura"]
            hum_vals = data["humedad"]

            if len(temp_vals) == 0 and len(hum_vals) == 0:
                continue

            # Calcular estadísticas
            temp_avg = sum(temp_vals) / len(temp_vals) if temp_vals else 0
            temp_max = max(temp_vals) if temp_vals else 0
            temp_min = min(temp_vals) if temp_vals else 0

            hum_avg = sum(hum_vals) / len(hum_vals) if hum_vals else 0
            hum_max = max(hum_vals) if hum_vals else 0
            hum_min = min(hum_vals) if hum_vals else 0

            indice = (temp_avg + hum_avg) / 2

            summary.append({
                "mes": month_key,
                "temperatura_promedio": round(temp_avg, 2),
                "temperatura_max": round(temp_max, 2),
                "temperatura_min": round(temp_min, 2),
                "humedad_promedio": round(hum_avg, 2),
                "humedad_max": round(hum_max, 2),
                "humedad_min": round(hum_min, 2),
                "n": len(temp_vals) + len(hum_vals),
                "indice": round(indice, 2),
                "year": data["year"],   
                "month": data["month"]  
            })

        # Ordenar por año y mes
        summary.sort(key=lambda x: (x["year"], x["month"]))

        # Generar notas
        if summary:
            mes_mas_caluroso = max(summary, key=lambda x: x["temperatura_promedio"])
            mes_mas_humedo = max(summary, key=lambda x: x["humedad_promedio"])
            mes_menos_propicio = min(summary, key=lambda x: x["indice"])

            notas = {
                "mes_mas_caluroso": {
                    "mes": mes_mas_caluroso["mes"],
                    "valor": mes_mas_caluroso["temperatura_promedio"],
                    "unidad": "°C"
                },
                "mes_mas_humedo": {
                    "mes": mes_mas_humedo["mes"],
                    "valor": mes_mas_humedo["humedad_promedio"],
                    "unidad": "%"
                },
                "mes_menos_propicio": {
                    "mes": mes_menos_propicio["mes"],
                    "valor": mes_menos_propicio["indice"],
                    "unidad": ""
                }
            }
        else:
            notas = {}

        # Construir respuesta con notas al comienzo
        response_data = {
            "notas": notas,
            "summary": [
                {
                    "mes": item["mes"],
                    "temperatura_promedio": item["temperatura_promedio"],
                    "temperatura_max": item["temperatura_max"],
                    "temperatura_min": item["temperatura_min"],
                    "humedad_promedio": item["humedad_promedio"],
                    "humedad_max": item["humedad_max"],
                    "humedad_min": item["humedad_min"],
                    "n": item["n"],
                    "indice": item["indice"]
                }
                for item in summary
            ]
        }

        return jsonify({
            "success": True,
            "data": response_data,
            "message": "Resumen mensual generado exitosamente"
        }), 200

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({
            "error": True,
            "message": f"Error al generar el resumen mensual: {str(e)}"
        }), 500