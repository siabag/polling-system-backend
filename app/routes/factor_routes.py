from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.factor_model import Factor
from app.models.possible_value_model import PossibleValue

# Crear Blueprint para las rutas de factores
factor_bp = Blueprint('factor', __name__)

# Endpoint para crear un nuevo factor
@factor_bp.route('/api/factors', methods=['POST'])
def create_factor():
    data = request.get_json()

    # Validar datos requeridos
    if not data or not data.get('nombre'):
        return jsonify({"msg": "Faltan datos requeridos"}), 400

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

    return jsonify({"msg": "Factor creado exitosamente", "factor": new_factor.to_dict()}), 201

# Endpoint para listar todos los factores
@factor_bp.route('/api/factors', methods=['GET'])
def list_factors():
    factors = Factor.query.all()
    return jsonify([factor.to_dict() for factor in factors]), 200

# Endpoint para obtener un factor específico
@factor_bp.route('/api/factors/<int:id>', methods=['GET'])
def get_factor(id):
    factor = Factor.query.get(id)
    if not factor:
        return jsonify({"msg": "Factor no encontrado"}), 404
    return jsonify(factor.to_dict()), 200

# Endpoint para actualizar un factor
@factor_bp.route('/api/factors/<int:id>', methods=['PUT'])
def update_factor(id):
    data = request.get_json()
    factor = Factor.query.get(id)

    if not factor:
        return jsonify({"msg": "Factor no encontrado"}), 404

    # Actualizar campos del factor
    factor.nombre = data.get('nombre', factor.nombre)
    factor.descripcion = data.get('descripcion', factor.descripcion)
    factor.categoria = data.get('categoria', factor.categoria)
    factor.tipo_encuesta_id = data.get('tipo_encuesta_id', factor.tipo_encuesta_id)

    # Guardar cambios en la base de datos
    db.session.commit()

    return jsonify({"msg": "Factor actualizado exitosamente", "factor": factor.to_dict()}), 200

# Endpoint para eliminar un factor
@factor_bp.route('/api/factors/<int:id>', methods=['DELETE'])
def delete_factor(id):
    factor = Factor.query.get(id)

    if not factor:
        return jsonify({"msg": "Factor no encontrado"}), 404

    # Eliminar el factor
    db.session.delete(factor)
    db.session.commit()

    return jsonify({"msg": "Factor eliminado exitosamente"}), 200

# Endpoint para agregar un valor posible a un factor
@factor_bp.route('/api/factors/<int:factor_id>/values', methods=['POST'])
def add_possible_value(factor_id):
    data = request.get_json()

    # Validar datos requeridos
    if not data or not data.get('valor'):
        return jsonify({"msg": "Faltan datos requeridos"}), 400

    # Buscar el factor
    factor = Factor.query.get(factor_id)
    if not factor:
        return jsonify({"msg": "Factor no encontrado"}), 404

    # Crear nuevo valor posible
    new_value = PossibleValue(valor=data['valor'], factor=factor)

    # Guardar en la base de datos
    db.session.add(new_value)
    db.session.commit()

    return jsonify({"msg": "Valor posible agregado exitosamente", "valor_posible": new_value.to_dict()}), 201

# Endpoint para listar todos los valores posibles de un factor
@factor_bp.route('/api/factors/<int:factor_id>/values', methods=['GET'])
def list_possible_values(factor_id):
    factor = Factor.query.get(factor_id)
    if not factor:
        return jsonify({"msg": "Factor no encontrado"}), 404

    return jsonify([value.to_dict() for value in factor.valores_posibles]), 200

# Endpoint para obtener un valor posible específico
@factor_bp.route('/api/factors/<int:factor_id>/values/<int:value_id>', methods=['GET'])
def get_possible_value(factor_id, value_id):
    factor = Factor.query.get(factor_id)
    if not factor:
        return jsonify({"msg": "Factor no encontrado"}), 404

    value = PossibleValue.query.get(value_id)
    if not value or value.factor_id != factor_id:
        return jsonify({"msg": "Valor posible no encontrado"}), 404

    return jsonify(value.to_dict()), 200

# Endpoint para actualizar un valor posible
@factor_bp.route('/api/factors/<int:factor_id>/values/<int:value_id>', methods=['PUT'])
def update_possible_value(factor_id, value_id):
    data = request.get_json()
    factor = Factor.query.get(factor_id)
    if not factor:
        return jsonify({"msg": "Factor no encontrado"}), 404

    value = PossibleValue.query.get(value_id)
    if not value or value.factor_id != factor_id:
        return jsonify({"msg": "Valor posible no encontrado"}), 404

    # Actualizar el valor posible
    value.valor = data.get('valor', value.valor)

    # Guardar cambios en la base de datos
    db.session.commit()

    return jsonify({"msg": "Valor posible actualizado exitosamente", "valor_posible": value.to_dict()}), 200

# Endpoint para eliminar un valor posible
@factor_bp.route('/api/factors/<int:factor_id>/values/<int:value_id>', methods=['DELETE'])
def delete_possible_value(factor_id, value_id):
    factor = Factor.query.get(factor_id)
    if not factor:
        return jsonify({"msg": "Factor no encontrado"}), 404

    value = PossibleValue.query.get(value_id)
    if not value or value.factor_id != factor_id:
        return jsonify({"msg": "Valor posible no encontrado"}), 404

    # Eliminar el valor posible
    db.session.delete(value)
    db.session.commit()

    return jsonify({"msg": "Valor posible eliminado exitosamente"}), 200