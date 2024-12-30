from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
from datetime import datetime

def check_media_access(media, user_identity, claims):
    """Helper funksjon for å sjekke tilgang til media"""
    # Admin har alltid tilgang
    if claims and claims.get('role') == 'admin':
        return True
        
    # Eier har alltid tilgang
    if media.uploaded_by == user_identity:
        return True
        
    # Public media er tilgjengelig for alle autentiserte brukere
    if media.visibility == "public":
        return True if user_identity else False
        
    # Private media er kun tilgjengelig for eier og admin
    return False

def check_album_access(album, user_identity, claims):
    """Helper funksjon for å sjekke tilgang til album"""
    # Admin har alltid tilgang
    if claims and claims.get('role') == 'admin':
        return True
        
    # Eier har alltid tilgang
    if album.created_by == User.query.filter_by(username=user_identity).first().id:
        return True
        
    # Public albums er tilgjengelig for alle autentiserte brukere
    if album.visibility == "public":
        return True if user_identity else False
        
    # Private albums er kun tilgjengelig for eier og admin
    return False

class MediaType(Enum):
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"

class GalleryMedia(db.Model):
    __tablename__ = 'gallery_media'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    media_type = db.Column(db.Enum(MediaType), nullable=False)
    content_type = db.Column(db.String(100), nullable=False)  # eks. image/jpeg, video/mp4
    file_size = db.Column(db.Integer)  # størrelse i bytes
    uploaded_by = db.Column(db.String(100), nullable=False)
    upload_time = db.Column(db.DateTime, server_default=db.func.now())
    visibility = db.Column(db.String(20), default="public")  # public, private
    likes = db.Column(db.Integer, default=0)
    tags = db.Column(db.JSON)  # For å lagre tags/kategorier

    # For bilder/video
    width = db.Column(db.Integer)  # bare for bilder/video
    height = db.Column(db.Integer)  # bare for bilder/video
    duration = db.Column(db.Float)  # bare for video (sekunder)
    thumbnail_url = db.Column(db.String(255))  # for video thumbnails

    def can_access(self, user_identity, claims):
        """Sjekk om brukeren har tilgang til dette mediet"""
        return check_media_access(self, user_identity, claims)

    def can_modify(self, user_identity, claims):
        """Sjekk om brukeren kan endre dette mediet"""
        return (claims and claims.get('role') == 'admin') or self.uploaded_by == user_identity

class GalleryComment(db.Model):
    __tablename__ = 'gallery_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.Integer, db.ForeignKey('gallery_media.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relasjoner
    media = db.relationship('GalleryMedia', backref=db.backref('comments', lazy=True))
    user = db.relationship('User', backref=db.backref('gallery_comments', lazy=True))

    def can_modify(self, user_identity, claims):
        """Sjekk om brukeren kan endre denne kommentaren"""
        return (claims and claims.get('role') == 'admin') or self.user.username == user_identity

class GalleryAlbum(db.Model):
    __tablename__ = 'gallery_albums'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    visibility = db.Column(db.String(20), default="public")
    cover_image_id = db.Column(db.Integer, db.ForeignKey('gallery_media.id'))

    # Relasjoner
    creator = db.relationship('User', backref=db.backref('albums', lazy=True))
    cover_image = db.relationship('GalleryMedia')

    def can_access(self, user_identity, claims):
        """Sjekk om brukeren har tilgang til dette albumet"""
        return check_album_access(self, user_identity, claims)

    def can_modify(self, user_identity, claims):
        """Sjekk om brukeren kan endre dette albumet"""
        user = User.query.filter_by(username=user_identity).first()
        return (claims and claims.get('role') == 'admin') or (user and self.created_by == user.id)

class AlbumMedia(db.Model):
    __tablename__ = 'album_media'
    
    id = db.Column(db.Integer, primary_key=True)
    album_id = db.Column(db.Integer, db.ForeignKey('gallery_albums.id'), nullable=False)
    media_id = db.Column(db.Integer, db.ForeignKey('gallery_media.id'), nullable=False)
    position = db.Column(db.Integer)  # For å ordne medier i albumet
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relasjoner
    album = db.relationship('GalleryAlbum', backref=db.backref('media_items', lazy=True))
    media = db.relationship('GalleryMedia')

    def can_access(self, user_identity, claims):
        """Sjekk om brukeren har tilgang til dette album-mediet"""
        return self.album.can_access(user_identity, claims) and self.media.can_access(user_identity, claims)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    role = db.Column(db.String(20), default='user')  # admin, user

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Sjekk om brukeren er admin"""
        return self.role == 'admin'

class RSVP(db.Model):
    __tablename__ = 'rsvps'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    attending = db.Column(db.Boolean, nullable=False)
    allergies = db.Column(db.String(255))

class Info(db.Model):
    __tablename__ = 'info'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

class FAQ(db.Model):
    __tablename__ = 'faq'
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)