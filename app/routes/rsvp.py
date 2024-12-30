from flask import Blueprint, request, jsonify
from app.models import db, RSVP
from flask_jwt_extended import jwt_required

rsvp_bp = Blueprint('rsvp', __name__, url_prefix="/rsvp")

@rsvp_bp.route('', methods=['POST'])
def create_rsvp():
    """
    Create a new RSVP
    ---
    tags:
      - RSVP
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - attending
          properties:
            name:
              type: string
              example: "John Doe"
            email:
              type: string
              example: "john@example.com"
            attending:
              type: boolean
              example: true
            allergies:
              type: string
              example: "Nuts, shellfish"
    responses:
      201:
        description: RSVP created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "RSVP created successfully"
            rsvp:
              type: object
              properties:
                id:
                  type: integer
                name:
                  type: string
                email:
                  type: string
                attending:
                  type: boolean
                allergies:
                  type: string
      400:
        description: Bad request (missing or invalid data)
    """
    data = request.get_json()
    
    if not data or not all(k in data for k in ('name', 'email', 'attending')):
        return jsonify({"message": "Name, email and attending status are required"}), 400

    existing_rsvp = RSVP.query.filter_by(email=data['email']).first()
    if existing_rsvp:
        return jsonify({"message": "RSVP already exists for this email"}), 400

    rsvp = RSVP(
        name=data['name'],
        email=data['email'],
        attending=data['attending'],
        allergies=data.get('allergies', '')
    )
    
    db.session.add(rsvp)
    db.session.commit()

    return jsonify({
        "message": "RSVP created successfully",
        "rsvp": {
            "id": rsvp.id,
            "name": rsvp.name,
            "email": rsvp.email,
            "attending": rsvp.attending,
            "allergies": rsvp.allergies
        }
    }), 201

@rsvp_bp.route('', methods=['GET'])
@jwt_required()
def get_rsvps():
    """
    Get all RSVPs
    ---
    tags:
      - RSVP
    security:
      - Bearer: []
    responses:
      200:
        description: List of all RSVPs
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              email:
                type: string
              attending:
                type: boolean
              allergies:
                type: string
      401:
        description: Unauthorized access
    """
    rsvps = RSVP.query.all()
    return jsonify([{
        "id": r.id,
        "name": r.name,
        "email": r.email,
        "attending": r.attending,
        "allergies": r.allergies
    } for r in rsvps])

@rsvp_bp.route('/<int:rsvp_id>', methods=['GET'])
@jwt_required()
def get_rsvp(rsvp_id):
    """
    Get a specific RSVP by ID
    ---
    tags:
      - RSVP
    security:
      - Bearer: []
    parameters:
      - name: rsvp_id
        in: path
        type: integer
        required: true
        description: ID of the RSVP to retrieve
    responses:
      200:
        description: RSVP details
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
            email:
              type: string
            attending:
              type: boolean
            allergies:
              type: string
      404:
        description: RSVP not found
    """
    rsvp = RSVP.query.get_or_404(rsvp_id)
    return jsonify({
        "id": rsvp.id,
        "name": rsvp.name,
        "email": rsvp.email,
        "attending": rsvp.attending,
        "allergies": rsvp.allergies
    })

@rsvp_bp.route('/<int:rsvp_id>', methods=['PUT'])
@jwt_required()
def update_rsvp(rsvp_id):
    """
    Update an existing RSVP
    ---
    tags:
      - RSVP
    security:
      - Bearer: []
    parameters:
      - name: rsvp_id
        in: path
        type: integer
        required: true
        description: ID of the RSVP to update
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            attending:
              type: boolean
            allergies:
              type: string
    responses:
      200:
        description: RSVP updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
            rsvp:
              type: object
              properties:
                id:
                  type: integer
                name:
                  type: string
                email:
                  type: string
                attending:
                  type: boolean
                allergies:
                  type: string
      404:
        description: RSVP not found
    """
    rsvp = RSVP.query.get_or_404(rsvp_id)
    data = request.get_json()

    if 'attending' in data:
        rsvp.attending = data['attending']
    if 'allergies' in data:
        rsvp.allergies = data['allergies']

    db.session.commit()

    return jsonify({
        "message": "RSVP updated successfully",
        "rsvp": {
            "id": rsvp.id,
            "name": rsvp.name,
            "email": rsvp.email,
            "attending": rsvp.attending,
            "allergies": rsvp.allergies
        }
    })

@rsvp_bp.route('/<int:rsvp_id>', methods=['DELETE'])
@jwt_required()
def delete_rsvp(rsvp_id):
    """
    Delete an RSVP
    ---
    tags:
      - RSVP
    security:
      - Bearer: []
    parameters:
      - name: rsvp_id
        in: path
        type: integer
        required: true
        description: ID of the RSVP to delete
    responses:
      200:
        description: RSVP deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "RSVP deleted successfully"
      404:
        description: RSVP not found
    """
    rsvp = RSVP.query.get_or_404(rsvp_id)
    db.session.delete(rsvp)
    db.session.commit()
    return jsonify({"message": "RSVP deleted successfully"})