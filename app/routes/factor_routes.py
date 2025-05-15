# app/routes/factor_routes.py

from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.factor_model import Factor
from app.models.possible_value_model import PossibleValue

# Crear Blueprint para las rutas de factores
factor_bp = Blueprint('factor', __name__)

# Endpoint para crear un nuevo factor
@factor_bp.route('/api/factors', methods=['POST'])
def create_factor():
    try:
        data = request.get_json()

        # Validar datos requeridos
        if not data or not data.get('nombre'):
            return jsonify({
                "error": True,
                "message": "Faltan datos requeridos"
            }), 400

        # Crear nuevo factor
        new_factor = Factor(
            nombre=data['nombre'],
            descripcion=data.get('descripcion'),
            categoria=data.get('categoria'),
            tipo_encuesta_id=data.get('tipo_encuesta_id')
        )

        # Guardar en la base de datos
        db.session.add(new_factor)
        db.session.commit()

        return jsonify({
            "success": True,
            "data": new_factor.to_dict(),
            "message": "Factor creado exitosamente"
        }), 201

    except Exception as e:
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
        return jsonify({
            "success": True,
            "data": [factor.to_dict() for factor in factors],
            "message": "Factores obtenidos exitosamente"
        }), 200

    except Exception as e:
        return jsonify({
            "error": True,
            "message": f"Error al obtener los factores: {str(e)}"
        }), 500


# Endpoint para obtener un factor específico
@factor_bp.route('/api/factors/<int:id>', methods=['GET'])
def get_factor(id):
    try:
        factor = Factor.query.get(id)
        if not factor:
            return jsonify({
                "error": True,
                "message": "Factor no encontrado"
            }), 404

        return jsonify({
            "success": True,
            "data": factor.to_dict(),
            "message": "Factor obtenido exitosamente"
        }), 200

    except Exception as e:
        return jsonify({
            "error": True,
            "message": f"Error al obtener el factor: {str(e)}"
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

        # Guardar cambios en la base de datos
        db.session.commit()

        return jsonify({
            "success": True,
            "data": factor.to_dict(),
            "message": "Factor actualizado exitosamente"
        }), 200

    except Exception as e:
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

        # Eliminar el factor
        db.session.delete(factor)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Factor eliminado exitosamente"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al eliminar el factor: {str(e)}"
        }), 500


# Endpoint para agregar un valor posible a un factor
@factor_bp.route('/api/factors/<int:factor_id>/values', methods=['POST'])
def add_possible_value(factor_id):
    try:
        data = request.get_json()

        # Validar datos requeridos
        if not data or not data.get('valor') or not data.get('codigo'):
            return jsonify({
                "error": True,
                "message": "Faltan datos requeridos"
            }), 400

        # Buscar el factor
        factor = Factor.query.get(factor_id)
        if not factor:
            return jsonify({
                "error": True,
                "message": "Factor no encontrado"
            }), 404

        # Crear nuevo valor posible
        new_value = PossibleValue(
            valor=data['valor'],
            codigo=data['codigo'],
            descripcion=data.get('descripcion'),
            factor=factor
        )

        # Guardar en la base de datos
        db.session.add(new_value)
        db.session.commit()

        return jsonify({
            "success": True,
            "data": new_value.to_dict(),
            "message": "Valor posible agregado exitosamente"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al agregar el valor posible: {str(e)}"
        }), 500


# Endpoint para listar todos los valores posibles de un factor
@factor_bp.route('/api/factors/<int:factor_id>/values', methods=['GET'])
def list_possible_values(factor_id):
    try:
        factor = Factor.query.get(factor_id)
        if not factor:
            return jsonify({
                "error": True,
                "message": "Factor no encontrado"
            }), 404

        return jsonify({
            "success": True,
            "data": [value.to_dict() for value in factor.valores_posibles],
            "message": "Valores posibles obtenidos exitosamente"
        }), 200

    except Exception as e:
        return jsonify({
            "error": True,
            "message": f"Error al obtener los valores posibles: {str(e)}"
        }), 500


# Endpoint para obtener un valor posible específico
@factor_bp.route('/api/factors/<int:factor_id>/values/<int:value_id>', methods=['GET'])
def get_possible_value(factor_id, value_id):
    try:
        factor = Factor.query.get(factor_id)
        if not factor:
            return jsonify({
                "error": True,
                "message": "Factor no encontrado"
            }), 404

        value = PossibleValue.query.get(value_id)
        if not value or value.factor_id != factor_id:
            return jsonify({
                "error": True,
                "message": "Valor posible no encontrado"
            }), 404

        return jsonify({
            "success": True,
            "data": value.to_dict(),
            "message": "Valor posible obtenido exitosamente"
        }), 200

    except Exception as e:
        # Manejar errores inesperados
        return jsonify({
            "error": True,
            "message": f"Error al obtener el valor posible: {str(e)}"
        }), 500


# Endpoint para actualizar un valor posible
@factor_bp.route('/api/factors/<int:factor_id>/values/<int:value_id>', methods=['PUT'])
def update_possible_value(factor_id, value_id):
    try:
        data = request.get_json()
        factor = Factor.query.get(factor_id)
        if not factor:
            return jsonify({
                "error": True,
                "message": "Factor no encontrado"
            }), 404

        value = PossibleValue.query.get(value_id)
        if not value or value.factor_id != factor_id:
            return jsonify({
                "error": True,
                "message": "Valor posible no encontrado"
            }), 404

        # Actualizar el valor posible
        value.valor = data.get('valor', value.valor)
        value.codigo = data.get('codigo', value.codigo)
        value.descripcion = data.get('descripcion', value.descripcion)

        # Guardar cambios en la base de datos
        db.session.commit()

        return jsonify({
            "success": True,
            "data": value.to_dict(),
            "message": "Valor posible actualizado exitosamente"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al actualizar el valor posible: {str(e)}"
        }), 500


# Endpoint para eliminar un valor posible
@factor_bp.route('/api/factors/<int:factor_id>/values/<int:value_id>', methods=['DELETE'])
def delete_possible_value(factor_id, value_id):
    try:
        factor = Factor.query.get(factor_id)
        if not factor:
            return jsonify({
                "error": True,
                "message": "Factor no encontrado"
            }), 404

        value = PossibleValue.query.get(value_id)
        if not value or value.factor_id != factor_id:
            return jsonify({
                "error": True,
                "message": "Valor posible no encontrado"
            }), 404

        # Eliminar el valor posible
        db.session.delete(value)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Valor posible eliminado exitosamente"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al eliminar el valor posible: {str(e)}"
        }), 500