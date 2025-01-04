from flask import Blueprint, request, jsonify
from app.models import (
    db, GalleryMedia, GalleryComment, GalleryAlbum, 
    AlbumMedia, MediaType, User
)
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import os
from datetime import datetime
from werkzeug.utils import secure_filename

gallery_bp = Blueprint('gallery', __name__, url_prefix="/gallery")

@gallery_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_media():
    """
    Upload new media to gallery
    ---
    tags:
      - Gallery
    security:
      - Bearer: []
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: Media file to upload
      - in: formData
        name: title
        type: string
        required: true
        description: Title of the media
      - in: formData
        name: description
        type: string
        description: Description of the media
      - in: formData
        name: media_type
        type: string
        enum: [image, video, text]
        required: true
        description: Type of media
      - in: formData
        name: tags
        type: array
        items:
          type: string
        description: Tags for the media
      - in: formData
        name: visibility
        type: string
        enum: [public, private]
        default: public
        description: Visibility of the media
    responses:
      201:
        description: Media uploaded successfully
      401:
        description: Unauthorized
      403:
        description: Forbidden
    """
    if 'file' not in request.files:
        return jsonify({"message": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No file selected"}), 400

    username = get_jwt_identity()
    claims = get_jwt()
    
    # Bare admin kan laste opp med annen visibility enn public hvis ikke spesifisert
    visibility = request.form.get('visibility', 'public')
    if visibility == 'private' and claims.get('role') != 'admin':
        return jsonify({"message": "Only admin can upload private media"}), 403

    filename = secure_filename(file.filename)
    media_type = request.form.get('media_type', 'IMAGE').upper()
    
    if media_type not in [t.name for t in MediaType]:
        return jsonify({"message": f"Invalid media type. Must be one of: {[t.name for t in MediaType]}"}), 400

    upload_dir = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Lagre filen
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)
    
    # Generer URL til filen
    base_url = request.host_url  # Base URL til applikasjonen
    file_url = f"{base_url}uploads/{filename}"

    media = GalleryMedia(
        title=request.form.get('title'),
        description=request.form.get('description'),
        filename=filename,
        media_type=MediaType[media_type],
        content_type=file.content_type,
        file_size=len(file.read()),
        uploaded_by=username,
        visibility=visibility,
        tags=request.form.getlist('tags')
    )

    db.session.add(media)
    db.session.commit()

    return jsonify({
        "message": "Media uploaded successfully",
        "media": {
            "id": media.id,
            "title": media.title,
            "filename": media.filename,
            "url": file_url,  # Legger til URL
            "media_type": media.media_type.value,
            "uploaded_by": media.uploaded_by,
            "upload_time": media.upload_time.isoformat(),
            "description": media.description,
            "tags": media.tags,
            "visibility": media.visibility
        }
    }), 201


@gallery_bp.route('/media', methods=['GET'])
@jwt_required(optional=True)
def get_gallery():
    """
    Get all accessible media
    ---
    tags:
      - Gallery
    parameters:
      - name: type
        in: query
        type: string
        enum: [image, video, text]
        description: Filter by media type
      - name: visibility
        in: query
        type: string
        enum: [public, private]
        description: Filter by visibility
      - name: tags
        in: query
        type: array
        items:
          type: string
        description: Filter by tags
    responses:
      200:
        description: List of accessible media
    """
    user_identity = get_jwt_identity()
    claims = get_jwt() if user_identity else None

    query = GalleryMedia.query

    # Filtrer basert på brukerens tilgang
    if not claims or claims.get('role') != 'admin':
        if user_identity:
            # Vis public og egne private medier
            query = query.filter(
                (GalleryMedia.visibility == "public") | 
                (GalleryMedia.uploaded_by == user_identity)
            )
        else:
            # Vis kun public medier for ikke-innloggede brukere
            query = query.filter(GalleryMedia.visibility == "public")

    # Filtrer på media type
    media_type = request.args.get('type')
    if media_type:
        query = query.filter(GalleryMedia.media_type == MediaType[media_type.upper()])

    # Filtrer på tags
    tags = request.args.getlist('tags')
    if tags:
        for tag in tags:
            query = query.filter(GalleryMedia.tags.contains([tag]))

    # Generer URL-er og returner data
    media = query.all()
    return jsonify([{
        "id": m.id,
        "title": m.title,
        "filename": m.filename,
        "url": f"{request.host_url}uploads/{m.filename}",
        "media_type": m.media_type.value,
        "uploaded_by": m.uploaded_by,
        "upload_time": m.upload_time.isoformat(),
        "description": m.description,
        "tags": m.tags,
        "visibility": m.visibility,
        "likes": m.likes,
        "comments": [{
            "id": c.id,
            "comment": c.comment,
            "user": c.user.username,
            "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat() if c.updated_at else None
        } for c in m.comments],
        "comment_count": len(m.comments)
    } for m in media])

    """
    Get all accessible media
    ---
    tags:
      - Gallery
    parameters:
      - name: type
        in: query
        type: string
        enum: [image, video, text]
        description: Filter by media type
      - name: visibility
        in: query
        type: string
        enum: [public, private]
        description: Filter by visibility
      - name: tags
        in: query
        type: array
        items:
          type: string
        description: Filter by tags
    responses:
      200:
        description: List of accessible media
    """
    user_identity = get_jwt_identity()
    claims = get_jwt() if user_identity else None

    query = GalleryMedia.query

    # Filtrer basert på brukerens tilgang
    if not claims or claims.get('role') != 'admin':
        if user_identity:
            # Vis public og egne private medier
            query = query.filter(
                (GalleryMedia.visibility == "public") | 
                (GalleryMedia.uploaded_by == user_identity)
            )
        else:
            # Vis kun public medier for ikke-innloggede brukere
            query = query.filter(GalleryMedia.visibility == "public")

    # Filtrer på media type
    media_type = request.args.get('type')
    if media_type:
        query = query.filter(GalleryMedia.media_type == MediaType[media_type.upper()])

    # Filtrer på tags
    tags = request.args.getlist('tags')
    if tags:
        for tag in tags:
            query = query.filter(GalleryMedia.tags.contains([tag]))

    media = query.all()
    return jsonify([{
        "id": m.id,
        "title": m.title,
        "filename": m.filename,
        "media_type": m.media_type.value,
        "uploaded_by": m.uploaded_by,
        "upload_time": m.upload_time.isoformat(),
        "description": m.description,
        "tags": m.tags,
        "visibility": m.visibility,
        "likes": m.likes
    } for m in media])

@gallery_bp.route('/media/<int:media_id>', methods=['GET'])
@jwt_required(optional=True)
def get_media(media_id):
    """
    Get specific media details
    ---
    tags:
      - Gallery
    parameters:
      - name: media_id
        in: path
        type: integer
        required: true
        description: ID of the media to retrieve
    responses:
      200:
        description: Media details
      403:
        description: Forbidden
      404:
        description: Media not found
    """
    media = GalleryMedia.query.get_or_404(media_id)
    user_identity = get_jwt_identity()
    claims = get_jwt() if user_identity else None

    if not media.can_access(user_identity, claims):
        return jsonify({"message": "Access denied"}), 403

    return jsonify({
        "id": media.id,
        "title": media.title,
        "filename": media.filename,
        "media_type": media.media_type.value,
        "uploaded_by": media.uploaded_by,
        "upload_time": media.upload_time.isoformat(),
        "description": media.description,
        "tags": media.tags,
        "visibility": media.visibility,
        "likes": media.likes,
        "comments": [{
            "id": c.id,
            "comment": c.comment,
            "user": c.user.username,
            "created_at": c.created_at.isoformat()
        } for c in media.comments]
    })

@gallery_bp.route('/media/<int:media_id>', methods=['PUT'])
@jwt_required()
def update_media(media_id):
    """
    Update media details
    ---
    tags:
      - Gallery
    security:
      - Bearer: []
    parameters:
      - name: media_id
        in: path
        type: integer
        required: true
        description: ID of the media to update
      - in: body
        name: media
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            description:
              type: string
            tags:
              type: array
              items:
                type: string
            visibility:
              type: string
              enum: [public, private]
    responses:
      200:
        description: Media updated successfully
      403:
        description: Forbidden
      404:
        description: Media not found
    """
    media = GalleryMedia.query.get_or_404(media_id)
    username = get_jwt_identity()
    claims = get_jwt()

    if not media.can_modify(username, claims):
        return jsonify({"message": "Only owner or admin can update media"}), 403

    data = request.get_json()
    
    if 'title' in data:
        media.title = data['title']
    if 'description' in data:
        media.description = data['description']
    if 'tags' in data:
        media.tags = data['tags']
    if 'visibility' in data:
        if media.uploaded_by != username and claims.get('role') != 'admin':
            return jsonify({"message": "Only admin can change visibility of other's media"}), 403
        media.visibility = data['visibility']

    db.session.commit()

    return jsonify({
        "message": "Media updated successfully",
        "media": {
            "id": media.id,
            "title": media.title,
            "description": media.description,
            "tags": media.tags,
            "visibility": media.visibility
        }
    })

@gallery_bp.route('/media/<int:media_id>', methods=['DELETE'])
@jwt_required()
def delete_media(media_id):
    """
    Delete media
    ---
    tags:
      - Gallery
    security:
      - Bearer: []
    parameters:
      - name: media_id
        in: path
        type: integer
        required: true
        description: ID of the media to delete
    responses:
      200:
        description: Media deleted successfully
      403:
        description: Forbidden
      404:
        description: Media not found
    """
    media = GalleryMedia.query.get_or_404(media_id)
    username = get_jwt_identity()
    claims = get_jwt()

    if not media.can_modify(username, claims):
        return jsonify({"message": "Only owner or admin can delete media"}), 403

    # Slett fil fra filsystemet
    try:
        file_path = os.path.join(os.getcwd(), 'uploads', media.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        # Logg feilen, men fortsett med å slette fra databasen
        print(f"Error deleting file: {str(e)}")

    db.session.delete(media)
    db.session.commit()

    return jsonify({"message": "Media deleted successfully"})

@gallery_bp.route('/media/<int:media_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(media_id):
    """
    Add comment to media
    ---
    tags:
      - Gallery
    security:
      - Bearer: []
    parameters:
      - name: media_id
        in: path
        type: integer
        required: true
      - in: body
        name: comment
        required: true
        schema:
          type: object
          required:
            - comment
          properties:
            comment:
              type: string
    responses:
      201:
        description: Comment added successfully
      403:
        description: Forbidden
      404:
        description: Media not found
    """
    media = GalleryMedia.query.get_or_404(media_id)
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    claims = get_jwt()

    # Sjekk om brukeren har tilgang til å kommentere på mediet
    if not media.can_access(username, claims):
        return jsonify({"message": "Access denied"}), 403
    
    data = request.get_json()
    comment = GalleryComment(
        media_id=media_id,
        user_id=user.id,
        comment=data['comment']
    )
    
    db.session.add(comment)
    db.session.commit()

    return jsonify({
        "message": "Comment added successfully",
        "comment": {
            "id": comment.id,
            "comment": comment.comment,
            "user": user.username,
            "created_at": comment.created_at.isoformat()
        }
    }), 201

@gallery_bp.route('/media/<int:media_id>/like', methods=['POST'])
@jwt_required()
def like_media(media_id):
    """
    Like/unlike media
    ---
    tags:
      - Gallery
    security:
      - Bearer: []
    parameters:
      - name: media_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Like status updated successfully
      403:
        description: Forbidden
      404:
        description: Media not found
    """
    media = GalleryMedia.query.get_or_404(media_id)
    username = get_jwt_identity()
    claims = get_jwt()

    # Sjekk om brukeren har tilgang til å like mediet
    if not media.can_access(username, claims):
        return jsonify({"message": "Access denied"}), 403

    media.likes += 1
    db.session.commit()

    return jsonify({
        "message": "Media liked successfully",
        "likes": media.likes
    })

@gallery_bp.route('/albums', methods=['POST'])
@jwt_required()
def create_album():
    """
    Create new album
    ---
    tags:
      - Gallery
    security:
      - Bearer: []
    parameters:
      - in: body
        name: album
        required: true
        schema:
          type: object
          required:
            - title
          properties:
            title:
              type: string
            description:
              type: string
            visibility:
              type: string
              enum: [public, private]
            media_ids:
              type: array
              items:
                type: integer
    responses:
      201:
        description: Album created successfully
      403:
        description: Forbidden
      404:
        description: One or more media items not found
    """
    data = request.get_json()
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    claims = get_jwt()

    # Sjekk tilgang til alle media som skal legges til
    if 'media_ids' in data:
        for media_id in data['media_ids']:
            media = GalleryMedia.query.get(media_id)
            if not media:
                return jsonify({"message": f"Media with id {media_id} not found"}), 404
            if not media.can_access(username, claims):
                return jsonify({"message": f"Access denied to media with id {media_id}"}), 403

    album = GalleryAlbum(
        title=data['title'],
        description=data.get('description'),
        created_by=user.id,
        visibility=data.get('visibility', 'public')
    )
    
    db.session.add(album)
    db.session.flush()  # For å få album.id
    
    # Legg til medier i albumet
    for position, media_id in enumerate(data.get('media_ids', [])):
        album_media = AlbumMedia(
            album_id=album.id,
            media_id=media_id,
            position=position
        )
        db.session.add(album_media)

    db.session.commit()

    return jsonify({
        "message": "Album created successfully",
        "album": {
            "id": album.id,
            "title": album.title,
            "description": album.description,
            "visibility": album.visibility
        }
    }), 201

@gallery_bp.route('/albums', methods=['GET'])
@jwt_required(optional=True)
def get_albums():
    """
    Get all accessible albums
    ---
    tags:
      - Gallery
    parameters:
      - name: visibility
        in: query
        type: string
        enum: [public, private]
        description: Filter by visibility
    responses:
      200:
        description: List of accessible albums
    """
    user_identity = get_jwt_identity()
    claims = get_jwt() if user_identity else None
    query = GalleryAlbum.query

    # Filtrer basert på brukerens tilgang
    if not claims or claims.get('role') != 'admin':
        if user_identity:
            # Vis public og egne private albums
            user = User.query.filter_by(username=user_identity).first()
            query = query.filter(
                (GalleryAlbum.visibility == "public") | 
                (GalleryAlbum.created_by == user.id)
            )
        else:
            # Vis kun public albums for ikke-innloggede brukere
            query = query.filter(GalleryAlbum.visibility == "public")

    # Filtrer på visibility hvis spesifisert
    visibility = request.args.get('visibility')
    if visibility:
        query = query.filter(GalleryAlbum.visibility == visibility)

    albums = query.all()
    return jsonify([{
        "id": a.id,
        "title": a.title,
        "description": a.description,
        "created_by": a.creator.username,
        "created_at": a.created_at.isoformat(),
        "visibility": a.visibility,
        "media_count": len(a.media_items)
    } for a in albums])

@gallery_bp.route('/albums/<int:album_id>', methods=['GET'])
@jwt_required(optional=True)
def get_album(album_id):
    """
    Get specific album details
    ---
    tags:
      - Gallery
    parameters:
      - name: album_id
        in: path
        type: integer
        required: true
        description: ID of the album to retrieve
    responses:
      200:
        description: Album details
      403:
        description: Forbidden
      404:
        description: Album not found
    """
    album = GalleryAlbum.query.get_or_404(album_id)
    user_identity = get_jwt_identity()
    claims = get_jwt() if user_identity else None

    if not album.can_access(user_identity, claims):
        return jsonify({"message": "Access denied"}), 403

    # Filtrer medier basert på tilgang
    accessible_media = [
        am for am in album.media_items 
        if am.media.can_access(user_identity, claims)
    ]

    return jsonify({
        "id": album.id,
        "title": album.title,
        "description": album.description,
        "created_by": album.creator.username,
        "created_at": album.created_at.isoformat(),
        "visibility": album.visibility,
        "media": [{
            "id": am.media.id,
            "title": am.media.title,
            "filename": am.media.filename,
            "media_type": am.media.media_type.value,
            "position": am.position
        } for am in sorted(accessible_media, key=lambda x: x.position)]
    })

@gallery_bp.route('/albums/<int:album_id>', methods=['PUT'])
@jwt_required()
def update_album(album_id):
    """
    Update album details
    ---
    tags:
      - Gallery
    security:
      - Bearer: []
    parameters:
      - name: album_id
        in: path
        type: integer
        required: true
        description: ID of the album to update
      - in: body
        name: album
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            description:
              type: string
            visibility:
              type: string
              enum: [public, private]
            media_ids:
              type: array
              items:
                type: integer
              description: New list of media IDs in desired order
    responses:
      200:
        description: Album updated successfully
      403:
        description: Forbidden
      404:
        description: Album or media not found
    """
    album = GalleryAlbum.query.get_or_404(album_id)
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    claims = get_jwt()

    if not album.can_modify(username, claims):
        return jsonify({"message": "Only owner or admin can update album"}), 403

    data = request.get_json()
    
    if 'title' in data:
        album.title = data['title']
    if 'description' in data:
        album.description = data['description']
    if 'visibility' in data:
        if album.created_by != user.id and claims.get('role') != 'admin':
            return jsonify({"message": "Only admin can change visibility of other's albums"}), 403
        album.visibility = data['visibility']
    
    # Oppdater media items hvis spesifisert
    if 'media_ids' in data:
        # Sjekk tilgang til alle nye media
        for media_id in data['media_ids']:
            media = GalleryMedia.query.get(media_id)
            if not media:
                return jsonify({"message": f"Media with id {media_id} not found"}), 404
            if not media.can_access(username, claims):
                return jsonify({"message": f"Access denied to media with id {media_id}"}), 403

        # Fjern eksisterende media items
        AlbumMedia.query.filter_by(album_id=album.id).delete()
        
        # Legg til nye media items med posisjoner
        for position, media_id in enumerate(data['media_ids']):
            album_media = AlbumMedia(
                album_id=album.id,
                media_id=media_id,
                position=position
            )
            db.session.add(album_media)

    db.session.commit()

    return jsonify({
        "message": "Album updated successfully",
        "album": {
            "id": album.id,
            "title": album.title,
            "description": album.description,
            "visibility": album.visibility
        }
    })

@gallery_bp.route('/albums/<int:album_id>', methods=['DELETE'])
@jwt_required()
def delete_album(album_id):
    """
    Delete album
    ---
    tags:
      - Gallery
    security:
      - Bearer: []
    parameters:
      - name: album_id
        in: path
        type: integer
        required: true
        description: ID of the album to delete
    responses:
      200:
        description: Album deleted successfully
      403:
        description: Forbidden
      404:
        description: Album not found
    """
    album = GalleryAlbum.query.get_or_404(album_id)
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    claims = get_jwt()

    if not album.can_modify(username, claims):
        return jsonify({"message": "Only owner or admin can delete album"}), 403

    db.session.delete(album)
    db.session.commit()

    return jsonify({"message": "Album deleted successfully"})

@gallery_bp.route('/search', methods=['GET'])
@jwt_required(optional=True)
def search_media():
    """
    Search media in gallery
    ---
    tags:
      - Gallery
    parameters:
      - name: q
        in: query
        type: string
        description: Search query for title and description
      - name: type
        in: query
        type: string
        enum: [image, video, text]
        description: Filter by media type
      - name: tags
        in: query
        type: array
        items:
          type: string
        collectionFormat: multi
        description: Filter by tags
      - name: uploaded_by
        in: query
        type: string
        description: Filter by uploader username
    responses:
      200:
        description: Search results
    """
    user_identity = get_jwt_identity()
    claims = get_jwt() if user_identity else None

    query = GalleryMedia.query

    # Filtrer basert på brukerens tilgang
    if not claims or claims.get('role') != 'admin':
        if user_identity:
            # Vis public og egne private medier
            query = query.filter(
                (GalleryMedia.visibility == "public") | 
                (GalleryMedia.uploaded_by == user_identity)
            )
        else:
            # Vis kun public medier for ikke-innloggede brukere
            query = query.filter(GalleryMedia.visibility == "public")

    # Søk i tittel og beskrivelse
    search_query = request.args.get('q')
    if search_query:
        query = query.filter(
            (GalleryMedia.title.ilike(f'%{search_query}%')) |
            (GalleryMedia.description.ilike(f'%{search_query}%'))
        )

    # Filtrer på media type
    media_type = request.args.get('type')
    if media_type:
        query = query.filter(GalleryMedia.media_type == MediaType[media_type.upper()])

    # Filtrer på tags
    tags = request.args.getlist('tags')
    if tags:
        for tag in tags:
            query = query.filter(GalleryMedia.tags.contains([tag]))

    # Filtrer på opplaster
    uploaded_by = request.args.get('uploaded_by')
    if uploaded_by:
        query = query.filter(GalleryMedia.uploaded_by == uploaded_by)

    media = query.order_by(GalleryMedia.upload_time.desc()).all()

    return jsonify([{
        "id": m.id,
        "title": m.title,
        "filename": m.filename,
        "media_type": m.media_type.value,
        "uploaded_by": m.uploaded_by,
        "upload_time": m.upload_time.isoformat(),
        "description": m.description,
        "tags": m.tags,
        "visibility": m.visibility,
        "likes": m.likes
    } for m in media])