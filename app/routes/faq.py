from flask import Blueprint, request, jsonify
from app.models import db, FAQ
from flask_jwt_extended import jwt_required

faq_bp = Blueprint('faq', __name__, url_prefix="/faq")

@faq_bp.route('', methods=['POST'])
@jwt_required()
def create_faq():
    """Oppretter nytt FAQ-spørsmål"""
    data = request.json
    faq = FAQ(
        question=data['question'],
        answer=data['answer']
    )
    db.session.add(faq)
    db.session.commit()
    return jsonify({"message": "FAQ created successfully"}), 201

@faq_bp.route('', methods=['GET'])
def get_faq():
    """Henter FAQ"""
    faq = FAQ.query.all()
    return jsonify([
        {"id": f.id, "question": f.question, "answer": f.answer} for f in faq
    ])
