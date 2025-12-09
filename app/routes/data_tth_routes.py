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
    
@data_tth_bp.route('/api/data_tth/alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    try:
        # Obtener parámetros de fecha
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        # Obtener parámetros de configuración de alertas
        temp_max = float(request.args.get('temp_max', '30'))
        temp_min = float(request.args.get('temp_min', '10'))
        hum_max = float(request.args.get('hum_max', '90'))
        hum_min = float(request.args.get('hum_min', '30'))

        # Si no se proporcionan fechas, usar el día anterior hasta el momento actual
        if not start_date_str or not end_date_str:
            now = datetime.now()  # Fecha y hora actual
            start_date = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)  # Inicio del día anterior
            end_date = now  # Hasta el momento actual
        else:
            # Convertir strings a objetos datetime
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59, microsecond=999999)

        # Convertir a cadenas en formato ISO 8601 para comparar con received_at
        start_date_iso = start_date.isoformat()
        end_date_iso = end_date.isoformat()

        # Consultar registros filtrando por rango de fechas
        query = DataTTH.query.filter(
            DataTTH.received_at.between(start_date_iso, end_date_iso)
        ).order_by(DataTTH.received_at.desc())

        records = query.all()

        if not records:
            return jsonify({
                "success": True,
                "data": {
                    "indicadores": {
                        "estado_hidrico": {
                            "semaforo": "GRIS",
                            "tendencia": "sin_datos",
                            "valor_actual": None,
                            "umbral_min": hum_min,
                            "umbral_max": hum_max
                        },
                        "indice_riesgo_fungico": {
                            "indice": 0,
                            "descripcion": "Mayor con HR alta y 18-24°C",
                            "semaforo": "GRIS"
                        },
                        "carga_salina": {
                            "ce_actual": None,
                            "tendencia": "sin_datos",
                            "umbral_max": 2.5
                        },
                        "acciones_pendientes": []
                    },
                    "alertas": {
                        "ambientales": [],
                        "humedad_suelo": [],
                        "conductividad_electrica": []
                    }
                },
                "message": "No se encontraron registros en el rango de fechas especificado"
            }), 200

        # Filtrar registros con fechas válidas en formato ISO 8601
        valid_records = []
        for record in records:
            try:
                # Intentar parsear la fecha en formato ISO 8601
                received_at = datetime.fromisoformat(record.received_at.replace('Z', '+00:00'))
                record.received_at_parsed = received_at  # Guardar la fecha parseada
                valid_records.append(record)
            except ValueError:
                # Omitir registros con fechas inválidas
                continue

        if not valid_records:
            return jsonify({
                "success": True,
                "data": {
                    "indicadores": {
                        "estado_hidrico": {
                            "semaforo": "GRIS",
                            "tendencia": "sin_datos",
                            "valor_actual": None,
                            "umbral_min": hum_min,
                            "umbral_max": hum_max
                        },
                        "indice_riesgo_fungico": {
                            "indice": 0,
                            "descripcion": "Mayor con HR alta y 18-24°C",
                            "semaforo": "GRIS"
                        },
                        "carga_salina": {
                            "ce_actual": None,
                            "tendencia": "sin_datos",
                            "umbral_max": 2.5
                        },
                        "acciones_pendientes": []
                    },
                    "alertas": {
                        "ambientales": [],
                        "humedad_suelo": [],
                        "conductividad_electrica": []
                    }
                },
                "message": "Todos los registros tienen fechas inválidas"
            }), 200

        # Obtener el último registro para evaluar las condiciones actuales
        latest_data = valid_records[0]  # El más reciente

        # Inicializar indicadores
        indicadores = {
            "estado_hidrico": {
                "semaforo": "VERDE",
                "tendencia": "estable",
                "valor_actual": None,
                "umbral_min": hum_min,
                "umbral_max": hum_max
            },
            "indice_riesgo_fungico": {
                "indice": 0,
                "descripcion": "Mayor con HR alta y 18-24°C",
                "semaforo": "VERDE"
            },
            "carga_salina": {
                "ce_actual": None,
                "tendencia": "estable",
                "umbral_max": 2.5
            },
            "acciones_pendientes": []
        }

        # Evaluar Estado Hídrico (Humedad del Suelo)
        if latest_data.water_SOIL is not None:
            indicadores["estado_hidrico"]["valor_actual"] = latest_data.water_SOIL

            if latest_data.water_SOIL < hum_min:
                indicadores["estado_hidrico"]["semaforo"] = "ROJO"
                indicadores["estado_hidrico"]["tendencia"] = "empeorando"
                indicadores["acciones_pendientes"].append("Implementar riegos adicionales.")
            elif latest_data.water_SOIL > hum_max:
                indicadores["estado_hidrico"]["semaforo"] = "AMARILLO"
                indicadores["estado_hidrico"]["tendencia"] = "mejorando"
                indicadores["acciones_pendientes"].append("Reducir frecuencia de riego.")
            else:
                indicadores["estado_hidrico"]["semaforo"] = "VERDE"
                indicadores["estado_hidrico"]["tendencia"] = "estable"

        # Evaluar Índice de Riesgo Fúngico
        if latest_data.Hum_SHT is not None and latest_data.TempC_SHT is not None:
            humedad = latest_data.Hum_SHT
            temperatura = latest_data.TempC_SHT

            # Condición: Humedad > 90% y Temperatura entre 18–24 °C
            if humedad > 90 and 18 <= temperatura <= 24:
                indicadores["indice_riesgo_fungico"]["indice"] = 1
                indicadores["indice_riesgo_fungico"]["semaforo"] = "NARANJA"
                indicadores["acciones_pendientes"].append("Ventilación en lotes y monitoreo focal de enfermedades.")
            else:
                indicadores["indice_riesgo_fungico"]["indice"] = 0
                indicadores["indice_riesgo_fungico"]["semaforo"] = "VERDE"

        # Evaluar Carga Salina (Conductividad Eléctrica)
        if latest_data.conduct_SOIL is not None:
            indicadores["carga_salina"]["ce_actual"] = latest_data.conduct_SOIL

            if latest_data.conduct_SOIL > 2.5:
                indicadores["carga_salina"]["semaforo"] = "ROJO"
                indicadores["carga_salina"]["tendencia"] = "empeorando"
                indicadores["acciones_pendientes"].append("Revisar prácticas de fertilización y drenaje.")
            else:
                indicadores["carga_salina"]["semaforo"] = "VERDE"
                indicadores["carga_salina"]["tendencia"] = "estable"

        # Generar Alertas
        alertas = {
            "ambientales": [],
            "humedad_suelo": [],
            "conductividad_electrica": []
        }

        # Alertas Ambientales
        if latest_data.TempC_SHT is not None:
            temperatura = latest_data.TempC_SHT

            # Alerta Amarilla - Estrés Térmico Moderado
            if temperatura > 26 and latest_data.Hum_SHT is not None and latest_data.Hum_SHT < 55:
                alertas["ambientales"].append({
                    "tipo": "Estrés Térmico Moderado",
                    "nivel": "amarillo",
                    "condicion": f"Temperatura > 26°C ({temperatura}°C) y Humedad Relativa < 55% ({latest_data.Hum_SHT}%)",
                    "accion_recomendada": "Incrementar frecuencia de riego y manejo temporal de sombra."
                })

            # Alerta Roja - Ola de Calor
            if temperatura > 30 and latest_data.Hum_SHT is not None and latest_data.Hum_SHT < 45:
                alertas["ambientales"].append({
                    "tipo": "Ola de Calor",
                    "nivel": "rojo",
                    "condicion": f"Temperatura > 30°C ({temperatura}°C) y Humedad Relativa < 45% ({latest_data.Hum_SHT}%)",
                    "accion_recomendada": "Riegos de emergencia y protección de plántulas."
                })

        # Alertas de Humedad del Suelo
        if latest_data.water_SOIL is not None:
            if latest_data.water_SOIL < hum_min:
                alertas["humedad_suelo"].append({
                    "tipo": "Déficit Hídrico",
                    "nivel": "amarillo",
                    "condicion": f"Humedad del suelo < {hum_min}% ({latest_data.water_SOIL}%)",
                    "accion_recomendada": "Implementar riegos adicionales."
                })

        # Alertas de Conductividad Eléctrica
        if latest_data.conduct_SOIL is not None:
            if latest_data.conduct_SOIL > 2.5:
                alertas["conductividad_electrica"].append({
                    "tipo": "Salinización",
                    "nivel": "rojo",
                    "condicion": f"Conductividad Eléctrica > 2.5 dS/m ({latest_data.conduct_SOIL} dS/m)",
                    "accion_recomendada": "Revisar prácticas de fertilización y drenaje."
                })

        # Construir respuesta
        response_data = {
            "indicadores": indicadores,
            "alertas": alertas
        }

        return jsonify({
            "success": True,
            "data": response_data,
            "message": "Alertas generadas exitosamente"
        }), 200

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({
            "error": True,
            "message": f"Error al generar las alertas: {str(e)}"
        }), 500