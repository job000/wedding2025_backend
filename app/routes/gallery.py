from flask import Blueprint, request, jsonify
from app.models import db, GalleryMedia
from flask_jwt_extended import jwt_required

gallery_bp = Blueprint('gallery', __name__, url_prefix="/gallery")

@gallery_bp.route('', methods=['POST'])
@jwt_required()
def upload_media():
    """Laster opp medieelementer"""
    data = request.json
    media = GalleryMedia(
        filename=data['filename'],
        uploaded_by=data['uploaded_by']
    )
    db.session.add(media)
    db.session.commit()
    return jsonify({"message": "Media uploaded successfully"}), 201

@gallery_bp.route('', methods=['GET'])
@jwt_required()
def get_gallery():
    """Henter galleriinnhold"""
    media = GalleryMedia.query.all()
    return jsonify([
        {
            "id": m.id,
            "filename": m.filename,
            "uploaded_by": m.uploaded_by,
            "upload_time": m.upload_time
        } for m in media
    ])
