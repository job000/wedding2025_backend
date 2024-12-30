from flask import Blueprint, request, jsonify
from app.models import db, Info
from flask_jwt_extended import jwt_required

info_bp = Blueprint('info', __name__, url_prefix="/info")

@info_bp.route('', methods=['POST'])
@jwt_required()
def create_info():
    """
    Create new information
    ---
    tags:
      - Information
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
            - content
          properties:
            title:
              type: string
              example: "Wedding Location"
            content:
              type: string
              example: "The wedding will be held at Beautiful Venue"
    responses:
      201:
        description: Information created successfully
        schema:
          type: object
          properties:
            message:
              type: string
            info:
              type: object
              properties:
                id:
                  type: integer
                title:
                  type: string
                content:
                  type: string
      400:
        description: Invalid request
    """
    data = request.get_json()
    if not data or not all(k in data for k in ('title', 'content')):
        return jsonify({"message": "Title and content are required"}), 400

    info = Info(
        title=data['title'],
        content=data['content']
    )
    db.session.add(info)
    db.session.commit()

    return jsonify({
        "message": "Info created successfully",
        "info": {
            "id": info.id,
            "title": info.title,
            "content": info.content
        }
    }), 201

@info_bp.route('', methods=['GET'])
def get_info():
    """
    Get all information
    ---
    tags:
      - Information
    responses:
      200:
        description: List of all information
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              title:
                type: string
              content:
                type: string
    """
    info = Info.query.all()
    return jsonify([{
        "id": i.id,
        "title": i.title,
        "content": i.content
    } for i in info])

@info_bp.route('/<int:info_id>', methods=['GET'])
def get_single_info(info_id):
    """
    Get specific information by ID
    ---
    tags:
      - Information
    parameters:
      - name: info_id
        in: path
        type: integer
        required: true
        description: ID of the information to retrieve
    responses:
      200:
        description: Information details
        schema:
          type: object
          properties:
            id:
              type: integer
            title:
              type: string
            content:
              type: string
      404:
        description: Information not found
    """
    info = Info.query.get_or_404(info_id)
    return jsonify({
        "id": info.id,
        "title": info.title,
        "content": info.content
    })

@info_bp.route('/<int:info_id>', methods=['PUT'])
@jwt_required()
def update_info(info_id):
    """
    Update existing information
    ---
    tags:
      - Information
    security:
      - Bearer: []
    parameters:
      - name: info_id
        in: path
        type: integer
        required: true
        description: ID of the information to update
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            content:
              type: string
    responses:
      200:
        description: Information updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
            info:
              type: object
              properties:
                id:
                  type: integer
                title:
                  type: string
                content:
                  type: string
      404:
        description: Information not found
    """
    info = Info.query.get_or_404(info_id)
    data = request.get_json()

    if 'title' in data:
        info.title = data['title']
    if 'content' in data:
        info.content = data['content']

    db.session.commit()

    return jsonify({
        "message": "Info updated successfully",
        "info": {
            "id": info.id,
            "title": info.title,
            "content": info.content
        }
    })

@info_bp.route('/<int:info_id>', methods=['DELETE'])
@jwt_required()
def delete_info(info_id):
    """
    Delete information
    ---
    tags:
      - Information
    security:
      - Bearer: []
    parameters:
      - name: info_id
        in: path
        type: integer
        required: true
        description: ID of the information to delete
    responses:
      200:
        description: Information deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Information deleted successfully"
      404:
        description: Information not found
    """
    info = Info.query.get_or_404(info_id)
    db.session.delete(info)
    db.session.commit()
    return jsonify({"message": "Information deleted successfully"})