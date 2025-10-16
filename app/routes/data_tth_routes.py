# app/routes/data_tth_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.data_tth_model import DataTTH
from app.extensions import db
from werkzeug.exceptions import NotFound, Forbidden
from datetime import datetime

# Crear Blueprint para las rutas de DataTTH
data_tth_bp = Blueprint('data_tth', __name__)

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
