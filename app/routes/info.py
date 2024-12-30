from flask import Blueprint, request, jsonify
from app.models import db, Info
from flask_jwt_extended import jwt_required

info_bp = Blueprint('info', __name__, url_prefix="/info")

@info_bp.route('', methods=['POST'])
@jwt_required()
def create_info():
    """Oppretter ny informasjon"""
    data = request.json
    info = Info(
        title=data['title'],
        content=data['content']
    )
    db.session.add(info)
    db.session.commit()
    return jsonify({"message": "Info created successfully"}), 201

@info_bp.route('', methods=['GET'])
def get_info():
    """Henter all informasjon"""
    info = Info.query.all()
    return jsonify([
        {"id": i.id, "title": i.title, "content": i.content} for i in info
    ])
