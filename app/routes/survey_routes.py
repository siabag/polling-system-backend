# app/routes/survey_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from app.extensions import db
from app.models.survey_model import Survey
from app.models.farm_model import Farm
from app.models.factor_model import Factor
from app.models.possible_value_model import PossibleValue
from app.models.response_factor_model import ResponseFactor
from app.models.survey_type_model import SurveyType

# Crear Blueprint para las rutas de encuestas
survey_bp = Blueprint('survey', __name__)

def get_encuesta_with_details(encuesta_id):
    encuesta = Survey.query.get(encuesta_id)
    if not encuesta:
        return None

    # Obtener datos relacionados
    tipo_encuesta = encuesta.tipo_encuesta
    finca = encuesta.finca

    return {
        "id": encuesta.id,
        "fecha_aplicacion": encuesta.fecha_aplicacion.isoformat(),
        "tipo_encuesta_id": encuesta.tipo_encuesta_id,
        "usuario_id": encuesta.usuario_id,
        "finca_id": encuesta.finca_id,
        "observaciones": encuesta.observaciones,
        "completada": encuesta.completada,
        "created_at": encuesta.created_at.isoformat(),
        "updated_at": encuesta.updated_at.isoformat() if encuesta.updated_at else None,
        "tipo_encuesta": {
            "id": tipo_encuesta.id,
            "nombre": tipo_encuesta.nombre,
            "descripcion": tipo_encuesta.descripcion,
            "activo": tipo_encuesta.activo,
            "created_at": tipo_encuesta.created_at.isoformat(),
            "updated_at": tipo_encuesta.updated_at.isoformat() if tipo_encuesta.updated_at else None
        } if tipo_encuesta else None,
        "finca": {
            "id": finca.id,
            "nombre": finca.nombre,
            "ubicacion": finca.ubicacion,
            "latitud": str(finca.latitud) if finca.latitud else None,
            "longitud": str(finca.longitud) if finca.longitud else None,
            "propietario": finca.propietario,
            "usuario_id": finca.usuario_id,
            "created_at": finca.created_at.isoformat(),
            "updated_at": finca.updated_at.isoformat() if finca.updated_at else None
        } if finca else None,
        "respuestas": [
            {
                "id": respuesta.id,
                "encuesta_id": respuesta.encuesta_id,
                "factor_id": respuesta.factor_id,
                "valor_posible_id": respuesta.valor_posible_id,
                "respuesta_texto": respuesta.respuesta_texto,
                "created_at": respuesta.created_at.isoformat(),
                "updated_at": respuesta.updated_at.isoformat() if respuesta.updated_at else None,
                "factor": {
                    "id": respuesta.factor.id,
                    "nombre": respuesta.factor.nombre,
                    "descripcion": respuesta.factor.descripcion,
                    "categoria": respuesta.factor.categoria,
                    "activo": respuesta.factor.activo,
                    "tipo_encuesta_id": respuesta.factor.tipo_encuesta_id,
                    "created_at": respuesta.factor.created_at.isoformat(),
                    "updated_at": respuesta.factor.updated_at.isoformat() if respuesta.factor.updated_at else None
                },
                "valor_posible": {
                    "id": respuesta.valor_posible.id,
                    "factor_id": respuesta.valor_posible.factor_id,
                    "valor": respuesta.valor_posible.valor,
                    "codigo": respuesta.valor_posible.codigo,
                    "descripcion": respuesta.valor_posible.descripcion,
                    "activo": respuesta.valor_posible.activo,
                    "created_at": respuesta.valor_posible.created_at.isoformat(),
                    "updated_at": respuesta.valor_posible.updated_at.isoformat() if respuesta.valor_posible.updated_at else None
                }
            }
            for respuesta in encuesta.respuestas
        ]
    }

# Endpoint para crear una nueva encuesta
@survey_bp.route('/api/encuestas', methods=['POST'])
@jwt_required()
def create_encuesta():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Validar datos mínimos
        required_fields = ['fecha_aplicacion', 'tipo_encuesta_id', 'finca_id']
        if not all(field in data for field in required_fields):
            return jsonify({
                "error": True,
                "message": "Faltan datos requeridos"
            }), 400

        # Convertir IDs a enteros
        tipo_encuesta_id = int(data['tipo_encuesta_id'])
        finca_id = int(data['finca_id'])

        # Verificar existencia de entidades relacionadas
        tipo_encuesta = SurveyType.query.filter_by(id=tipo_encuesta_id, activo=True).first()
        if not tipo_encuesta:
            return jsonify({
                "error": True,
                "message": "Tipo de encuesta no válido"
            }), 400

        finca = Farm.query.get(finca_id)
        if not finca:
            return jsonify({
                "error": True,
                "message": "Finca no encontrada"
            }), 404

        # Iniciar transacción
        with db.session.begin_nested():
            # Crear encuesta
            nueva_encuesta = Survey(
                fecha_aplicacion=data['fecha_aplicacion'],
                tipo_encuesta_id=tipo_encuesta_id,
                usuario_id=user_id,
                finca_id=finca_id,
                observaciones=data.get('observaciones', ''),
                completada=False
            )
            db.session.add(nueva_encuesta)
            db.session.flush()  # Para obtener el ID generado

            # Procesar respuestas si están presentes
            if 'respuestas' in data and data['respuestas']:
                factor_ids = [resp['factor_id'] for resp in data['respuestas']]
                factores = Factor.query.filter(Factor.id.in_(factor_ids), Factor.activo == True).all()
                factores_map = {f.id: f for f in factores}

                valores = PossibleValue.query.filter(
                    PossibleValue.factor_id.in_(factor_ids),
                    PossibleValue.activo == True
                ).all()
                valores_map = {}
                for v in valores:
                    if v.factor_id not in valores_map:
                        valores_map[v.factor_id] = {}
                    valores_map[v.factor_id][v.id] = v

                for resp in data['respuestas']:
                    factor_id = int(resp['factor_id'])
                    valor_id = int(resp['valor_posible_id'])

                    # Validar factor
                    if factor_id not in factores_map:
                        return jsonify({
                            "error": True,
                            "message": f"Factor {factor_id} no válido para este tipo"
                        }), 400

                    # Validar valor
                    if factor_id not in valores_map or valor_id not in valores_map[factor_id]:
                        return jsonify({
                            "error": True,
                            "message": f"Valor {valor_id} no válido para factor {factor_id}"
                        }), 400

                    # Crear respuesta
                    nueva_respuesta = ResponseFactor(
                        encuesta_id=nueva_encuesta.id,
                        factor_id=factor_id,
                        valor_posible_id=valor_id,
                        respuesta_texto=resp.get('respuesta_texto', '')
                    )
                    db.session.add(nueva_respuesta)

        # Confirmar la transacción principal
        db.session.commit()

        # Retornar datos de la encuesta creada
        encuesta_data = get_encuesta_with_details(nueva_encuesta.id)
        return jsonify({
            "success": True,
            "data": encuesta_data,
            "message": "Encuesta creada exitosamente"
        }), 201

    except ValueError as e:
        return jsonify({
            "error": True,
            "message": f"Datos inválidos: {str(e)}"
        }), 400

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al crear la encuesta: {str(e)}"
        }), 500


# Endpoint para listar todas las encuestas de un usuario
@survey_bp.route('/api/encuestas', methods=['GET'])
@jwt_required()
def list_encuestas():
    try:
        user_id = get_jwt_identity()

        # Obtener parámetros de paginación y filtros
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('limit', 10, type=int)
        tipo_encuesta_id = request.args.get('tipo_encuesta_id', None, type=int)
        finca_id = request.args.get('finca_id', None,type=int)
        fecha_desde = request.args.get('fecha_desde', None)
        fecha_hasta = request.args.get('fecha_hasta', None)
        completada = request.args.get('completada', type=lambda v: v.lower() == 'true')

        # Construir query base
        query = Survey.query.filter_by(usuario_id=user_id)

        # Aplicar filtros
        if tipo_encuesta_id is not None:
            query = query.filter_by(tipo_encuesta_id=tipo_encuesta_id)
        
        if finca_id is not None:
            query = query.filter_by(finca_id=finca_id)
        
        if fecha_desde:
            try:
                fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                query = query.filter(Survey.fecha_aplicacion >= fecha_desde_dt)
            except ValueError:
                return jsonify({
                    "error": True,
                    "message": "Formato de fecha desde inválido. Use YYYY-MM-DD"
                }), 400
        
        if fecha_hasta:
            try:
                fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                query = query.filter(Survey.fecha_aplicacion <= fecha_hasta_dt)
            except ValueError:
                return jsonify({
                    "error": True,
                    "message": "Formato de fecha hasta inválido. Use YYYY-MM-DD"
                }), 400
        
        if completada is not None:
            query = query.filter_by(completada=completada)

        # Paginar resultados
        pagination = query.order_by(Survey.fecha_aplicacion.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )

        return jsonify({
            "success": True,
            "data": [get_encuesta_with_details(encuesta.id) for encuesta in pagination.items],
            "total": pagination.total,
            "page": page,
            "totalPages": pagination.pages,
            "message": "Encuestas obtenidas exitosamente"
        }), 200

    except SQLAlchemyError as e:
        return jsonify({
            "error": True,
            "message": f"Error al obtener las encuestas: {str(e)}"
        }), 500


# Endpoint para obtener los detalles de una encuesta específica
@survey_bp.route('/api/encuestas/<int:encuesta_id>', methods=['GET'])
@jwt_required()
def get_encuesta(encuesta_id):
    try:
        user_id = get_jwt_identity()

        # Buscar la encuesta
        encuesta = Survey.query.get(encuesta_id)
        if not encuesta or encuesta.usuario_id != user_id:
            return jsonify({
                "error": True,
                "message": "Encuesta no encontrada o no autorizada"
            }), 404

        # Retornar detalles de la encuesta
        encuesta_data = get_encuesta_with_details(encuesta.id)
        return jsonify({
            "success": True,
            "data": encuesta_data,
            "message": "Encuesta obtenida exitosamente"
        }), 200

    except SQLAlchemyError as e:
        return jsonify({
            "error": True,
            "message": f"Error al obtener la encuesta: {str(e)}"
        }), 500


# Endpoint para actualizar una encuesta existente
@survey_bp.route('/api/encuestas/<int:encuesta_id>', methods=['PUT'])
@jwt_required()
def update_encuesta(encuesta_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Buscar la encuesta
        encuesta = Survey.query.get(encuesta_id)
        if not encuesta or encuesta.usuario_id != user_id:
            return jsonify({
                "error": True,
                "message": "Encuesta no encontrada o no autorizada"
            }), 404

        # Actualizar campos
        encuesta.fecha_aplicacion = data.get('fecha_aplicacion', encuesta.fecha_aplicacion)
        encuesta.observaciones = data.get('observaciones', encuesta.observaciones)
        encuesta.completada = data.get('completada', encuesta.completada)

        # Procesar respuestas si están presentes
        if 'respuestas' in data and data['respuestas']:
            factor_ids = [resp['factor_id'] for resp in data['respuestas']]
            factores = Factor.query.filter(Factor.id.in_(factor_ids), Factor.activo == True).all()
            factores_map = {f.id: f for f in factores}

            valores = PossibleValue.query.filter(
                PossibleValue.factor_id.in_(factor_ids),
                PossibleValue.activo == True
            ).all()
            valores_map = {}
            for v in valores:
                if v.factor_id not in valores_map:
                    valores_map[v.factor_id] = {}
                valores_map[v.factor_id][v.id] = v

            for resp in data['respuestas']:
                factor_id = int(resp['factor_id'])
                valor_id = int(resp['valor_posible_id'])

                # Validar factor
                if factor_id not in factores_map:
                    return jsonify({
                        "error": True,
                        "message": f"Factor {factor_id} no válido para este tipo"
                    }), 400

                # Validar valor
                if factor_id not in valores_map or valor_id not in valores_map[factor_id]:
                    return jsonify({
                        "error": True,
                        "message": f"Valor {valor_id} no válido para factor {factor_id}"
                    }), 400

                # Crear o actualizar respuesta
                respuesta = ResponseFactor.query.filter_by(
                    encuesta_id=encuesta.id,
                    factor_id=factor_id
                ).first()

                if respuesta:
                    respuesta.valor_posible_id = valor_id
                    respuesta.respuesta_texto = resp.get('respuesta_texto', respuesta.respuesta_texto)
                else:
                    nueva_respuesta = ResponseFactor(
                        encuesta_id=encuesta.id,
                        factor_id=factor_id,
                        valor_posible_id=valor_id,
                        respuesta_texto=resp.get('respuesta_texto', '')
                    )
                    db.session.add(nueva_respuesta)

        # Guardar cambios
        db.session.commit()

        # Retornar datos de la encuesta actualizada
        encuesta_data = get_encuesta_with_details(encuesta.id)
        return jsonify({
            "success": True,
            "data": encuesta_data,
            "message": "Encuesta actualizada exitosamente"
        }), 200

    except ValueError as e:
        return jsonify({
            "error": True,
            "message": f"Datos inválidos: {str(e)}"
        }), 400

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al actualizar la encuesta: {str(e)}"
        }), 500


# Endpoint para eliminar una encuesta
@survey_bp.route('/api/encuestas/<int:encuesta_id>', methods=['DELETE'])
@jwt_required()
def delete_encuesta(encuesta_id):
    try:
        user_id = get_jwt_identity()

        # Buscar la encuesta
        encuesta = Survey.query.get(encuesta_id)
        if not encuesta or encuesta.usuario_id != user_id:
            return jsonify({
                "error": True,
                "message": "Encuesta no encontrada o no autorizada"
            }), 404

        # Eliminar la encuesta dentro de una transacción
        with db.session.begin_nested():
            db.session.delete(encuesta)

        # Confirmar la transacción principal
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Encuesta eliminada exitosamente"
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al eliminar la encuesta: {str(e)}"
        }), 500