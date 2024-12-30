from flask import Blueprint, request, jsonify
from app.models import db, FAQ
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

faq_bp = Blueprint('faq', __name__, url_prefix="/faq")

@faq_bp.route('', methods=['POST'])
@jwt_required()
def create_faq():
    """
    Create new FAQ entry
    ---
    tags:
      - FAQ
    security:
      - Bearer: []
    parameters:
      - in: body
        name: faq
        required: true
        schema:
          type: object
          required:
            - question
            - answer
          properties:
            question:
              type: string
              example: "What time does the ceremony start?"
            answer:
              type: string
              example: "The ceremony starts at 2 PM sharp."
    responses:
      201:
        description: FAQ created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: FAQ created successfully
            faq:
              type: object
              properties:
                id:
                  type: integer
                question:
                  type: string
                answer:
                  type: string
      400:
        description: Invalid request
      401:
        description: Unauthorized
    """
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"message": "Admin access required"}), 403

    data = request.get_json()
    if not data or not all(k in data for k in ('question', 'answer')):
        return jsonify({"message": "Question and answer are required"}), 400

    faq = FAQ(
        question=data['question'],
        answer=data['answer']
    )
    db.session.add(faq)
    db.session.commit()

    return jsonify({
        "message": "FAQ created successfully",
        "faq": {
            "id": faq.id,
            "question": faq.question,
            "answer": faq.answer
        }
    }), 201

@faq_bp.route('', methods=['GET'])
def get_faq():
    """
    Get all FAQ entries
    ---
    tags:
      - FAQ
    responses:
      200:
        description: List of all FAQs
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              question:
                type: string
              answer:
                type: string
    """
    faqs = FAQ.query.all()
    return jsonify([{
        "id": f.id,
        "question": f.question,
        "answer": f.answer
    } for f in faqs])

@faq_bp.route('/<int:faq_id>', methods=['GET'])
def get_single_faq(faq_id):
    """
    Get specific FAQ by ID
    ---
    tags:
      - FAQ
    parameters:
      - name: faq_id
        in: path
        type: integer
        required: true
        description: ID of the FAQ to retrieve
    responses:
      200:
        description: FAQ details
        schema:
          type: object
          properties:
            id:
              type: integer
            question:
              type: string
            answer:
              type: string
      404:
        description: FAQ not found
    """
    faq = FAQ.query.get_or_404(faq_id)
    return jsonify({
        "id": faq.id,
        "question": faq.question,
        "answer": faq.answer
    })

@faq_bp.route('/<int:faq_id>', methods=['PUT'])
@jwt_required()
def update_faq(faq_id):
    """
    Update existing FAQ
    ---
    tags:
      - FAQ
    security:
      - Bearer: []
    parameters:
      - name: faq_id
        in: path
        type: integer
        required: true
        description: ID of the FAQ to update
      - in: body
        name: faq
        required: true
        schema:
          type: object
          properties:
            question:
              type: string
            answer:
              type: string
    responses:
      200:
        description: FAQ updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
            faq:
              type: object
              properties:
                id:
                  type: integer
                question:
                  type: string
                answer:
                  type: string
      404:
        description: FAQ not found
      403:
        description: Forbidden - admin access required
    """
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"message": "Admin access required"}), 403

    faq = FAQ.query.get_or_404(faq_id)
    data = request.get_json()

    if 'question' in data:
        faq.question = data['question']
    if 'answer' in data:
        faq.answer = data['answer']

    db.session.commit()

    return jsonify({
        "message": "FAQ updated successfully",
        "faq": {
            "id": faq.id,
            "question": faq.question,
            "answer": faq.answer
        }
    })

@faq_bp.route('/<int:faq_id>', methods=['DELETE'])
@jwt_required()
def delete_faq(faq_id):
    """
    Delete FAQ entry
    ---
    tags:
      - FAQ
    security:
      - Bearer: []
    parameters:
      - name: faq_id
        in: path
        type: integer
        required: true
        description: ID of the FAQ to delete
    responses:
      200:
        description: FAQ deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: FAQ deleted successfully
      404:
        description: FAQ not found
      403:
        description: Forbidden - admin access required
    """
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"message": "Admin access required"}), 403

    faq = FAQ.query.get_or_404(faq_id)
    db.session.delete(faq)
    db.session.commit()

    return jsonify({"message": "FAQ deleted successfully"})