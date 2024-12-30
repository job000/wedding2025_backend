from flask import Blueprint, request, jsonify
from app.models import db, RSVP
from flask_jwt_extended import jwt_required

rsvp_bp = Blueprint('rsvp', __name__, url_prefix="/rsvp")

@rsvp_bp.route('', methods=['POST'])
def create_rsvp():
    """Oppretter en ny RSVP"""
    data = request.json
    rsvp = RSVP(
        name=data['name'],
        email=data['email'],
        attending=data['attending'],
        allergies=data.get('allergies', '')
    )
    db.session.add(rsvp)
    db.session.commit()
    return jsonify({"message": "RSVP created successfully"}), 201

@rsvp_bp.route('', methods=['GET'])
@jwt_required()
def get_rsvps():
    """Henter alle RSVPs"""
    rsvps = RSVP.query.all()
    return jsonify([
        {
            "id": r.id,
            "name": r.name,
            "email": r.email,
            "attending": r.attending,
            "allergies": r.allergies
        } for r in rsvps
    ])
