# app/routes/factor_routes.py

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from app.models.factor_model import Factor
from app.models.possible_value_model import PossibleValue

# Crear Blueprint para las rutas de factores
factor_bp = Blueprint('factor', __name__)

# Endpoint para crear un nuevo factor con valores posibles
@factor_bp.route('/api/factors', methods=['POST'])
def create_factor():
    try:
        data = request.get_json()

        # Validar datos mínimos
        required_fields = ['nombre', 'descripcion', 'categoria', 'tipo_encuesta_id', 'valores_posibles']
        if not all(field in data for field in required_fields):
            return jsonify({
                "error": True,
                "message": "Faltan datos requeridos"
            }), 400

        # Validar valores posibles
        valores_posibles = data['valores_posibles']
        if not isinstance(valores_posibles, list) or len(valores_posibles) == 0:
            return jsonify({
                "error": True,
                "message": "Debe proporcionar al menos un valor posible"
            }), 400

        # Crear el factor dentro de una transacción
        with db.session.begin_nested():
            new_factor = Factor(
                nombre=data['nombre'],
                descripcion=data['descripcion'],
                categoria=data['categoria'],
                tipo_encuesta_id=data['tipo_encuesta_id']
            )
            db.session.add(new_factor)
            db.session.flush()  # Para obtener el ID generado

            # Crear valores posibles asociados
            for valor_data in valores_posibles:
                if not all(key in valor_data for key in ['valor', 'codigo', 'descripcion']):
                    return jsonify({
                        "error": True,
                        "message": "Datos inválidos en valores posibles"
                    }), 400

                new_value = PossibleValue(
                    valor=valor_data['valor'],
                    codigo=valor_data['codigo'],
                    descripcion=valor_data['descripcion'],
                    factor_id=new_factor.id
                )
                db.session.add(new_value)

        # Confirmar la transacción principal
        db.session.commit()

        return jsonify({
            "success": True,
            "data": {
                "id": new_factor.id,
                "nombre": new_factor.nombre,
                "descripcion": new_factor.descripcion,
                "categoria": new_factor.categoria,
                "tipo_encuesta_id": new_factor.tipo_encuesta_id,
                "valores_posibles": [
                    {
                        "id": value.id,
                        "valor": value.valor,
                        "codigo": value.codigo,
                        "descripcion": value.descripcion
                    }
                    for value in new_factor.valores_posibles
                ]
            },
            "message": "Factor creado exitosamente"
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al crear el factor: {str(e)}"
        }), 500


# Endpoint para listar todos los factores
@factor_bp.route('/api/factors', methods=['GET'])
def list_factors():
    try:
        factors = Factor.query.all()
        result = [
            {
                "id": factor.id,
                "nombre": factor.nombre,
                "descripcion": factor.descripcion,
                "categoria": factor.categoria,
                "tipo_encuesta_id": factor.tipo_encuesta_id,
                "valores_posibles": [
                    {
                        "id": value.id,
                        "valor": value.valor,
                        "codigo": value.codigo,
                        "descripcion": value.descripcion
                    }
                    for value in factor.valores_posibles
                ]
            }
            for factor in factors
        ]

        return jsonify({
            "success": True,
            "data": result,
            "message": "Factores obtenidos exitosamente"
        }), 200

    except SQLAlchemyError as e:
        return jsonify({
            "error": True,
            "message": f"Error al obtener los factores: {str(e)}"
        }), 500


# Endpoint para actualizar un factor
@factor_bp.route('/api/factors/<int:id>', methods=['PUT'])
def update_factor(id):
    try:
        data = request.get_json()
        factor = Factor.query.get(id)

        if not factor:
            return jsonify({
                "error": True,
                "message": "Factor no encontrado"
            }), 404

        # Actualizar campos del factor
        factor.nombre = data.get('nombre', factor.nombre)
        factor.descripcion = data.get('descripcion', factor.descripcion)
        factor.categoria = data.get('categoria', factor.categoria)
        factor.tipo_encuesta_id = data.get('tipo_encuesta_id', factor.tipo_encuesta_id)

        # Actualizar valores posibles si están presentes
        if 'valores_posibles' in data:
            nuevos_valores = data['valores_posibles']

            # Eliminar valores existentes
            PossibleValue.query.filter_by(factor_id=factor.id).delete()

            # Crear nuevos valores posibles
            for valor_data in nuevos_valores:
                if not all(key in valor_data for key in ['valor', 'codigo', 'descripcion']):
                    return jsonify({
                        "error": True,
                        "message": "Datos inválidos en valores posibles"
                    }), 400

                new_value = PossibleValue(
                    valor=valor_data['valor'],
                    codigo=valor_data['codigo'],
                    descripcion=valor_data['descripcion'],
                    factor_id=factor.id
                )
                db.session.add(new_value)

        # Guardar cambios
        db.session.commit()

        return jsonify({
            "success": True,
            "data": {
                "id": factor.id,
                "nombre": factor.nombre,
                "descripcion": factor.descripcion,
                "categoria": factor.categoria,
                "tipo_encuesta_id": factor.tipo_encuesta_id,
                "valores_posibles": [
                    {
                        "id": value.id,
                        "valor": value.valor,
                        "codigo": value.codigo,
                        "descripcion": value.descripcion
                    }
                    for value in factor.valores_posibles
                ]
            },
            "message": "Factor actualizado exitosamente"
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al actualizar el factor: {str(e)}"
        }), 500


# Endpoint para eliminar un factor
@factor_bp.route('/api/factors/<int:id>', methods=['DELETE'])
def delete_factor(id):
    try:
        factor = Factor.query.get(id)

        if not factor:
            return jsonify({
                "error": True,
                "message": "Factor no encontrado"
            }), 404

        # Eliminar el factor y sus valores posibles asociados
        with db.session.begin_nested():
            PossibleValue.query.filter_by(factor_id=factor.id).delete()
            db.session.delete(factor)

        # Confirmar la transacción principal
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Factor eliminado exitosamente"
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al eliminar el factor: {str(e)}"
        }), 500
    
# Endpoint para obtener el detalle de un factor
@factor_bp.route('/api/factors/<int:id>', methods=['GET'])
def get_factor(id):
    try:
        # Buscar el factor por ID
        factor = Factor.query.get(id)

        if not factor:
            return jsonify({
                "error": True,
                "message": "Factor no encontrado"
            }), 404

        # Formatear los datos del factor y sus valores posibles
        factor_data = {
            "id": factor.id,
            "nombre": factor.nombre,
            "descripcion": factor.descripcion,
            "categoria": factor.categoria,
            "activo": factor.activo,
            "tipo_encuesta_id": factor.tipo_encuesta_id,
            "created_at": factor.created_at.isoformat(),
            "updated_at": factor.updated_at.isoformat() if factor.updated_at else None,
            "valores_posibles": [
                {
                    "id": value.id,
                    "factor_id": value.factor_id,
                    "valor": value.valor,
                    "codigo": value.codigo,
                    "descripcion": value.descripcion,
                    "activo": value.activo,
                    "created_at": value.created_at.isoformat(),
                    "updated_at": value.updated_at.isoformat() if value.updated_at else None
                }
                for value in factor.valores_posibles
            ]
        }

        return jsonify({
            "success": True,
            "data": factor_data,
            "message": "Factor obtenido exitosamente"
        }), 200

    except SQLAlchemyError as e:
        return jsonify({
            "error": True,
            "message": f"Error al obtener el factor: {str(e)}"
        }), 500