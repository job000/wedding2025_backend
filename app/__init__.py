from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flasgger import Swagger

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    # Logg JWT_SECRET_KEY
    print(f"JWT_SECRET_KEY: {app.config['JWT_SECRET_KEY']}")

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return jsonify({
            'msg': 'Token har utløpt',
            'error': 'token_expired'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'msg': 'Signaturen validering feilet',
            'error': 'invalid_token'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'msg': 'Authorization header mangler',
            'error': 'authorization_header_missing'
        }), 401

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_data):
        return jsonify({
            'msg': 'Token er ikke fersk lenger',
            'error': 'fresh_token_required'
        }), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_data):
        return jsonify({
            'msg': 'Token har blitt tilbakekalt',
            'error': 'token_revoked'
        }), 401

    # Swagger template configuration
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Wedding App API",
            "description": "API for Wedding Application",
            "version": "1.0.0",
            "contact": {
                "name": "John Michael & Frida",
                "url": "http://fridaogjohnmichael.no"
            }
        },
        "basePath": "/",
        "schemes": [
            "http",
            "https"
        ],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Bearer {token}\""
            }
        },
        "security": [
            {
                "Bearer": []
            }
        ],
        "definitions": {
            "User": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "example": "testuser"
                    },
                    "role": {
                        "type": "string",
                        "enum": ["user", "admin"],
                        "example": "user"
                    }
                }
            },
            "RSVP": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "example": 1
                    },
                    "name": {
                        "type": "string",
                        "example": "John Doe"
                    },
                    "email": {
                        "type": "string",
                        "example": "john@example.com"
                    },
                    "attending": {
                        "type": "boolean",
                        "example": True
                    },
                    "allergies": {
                        "type": "string",
                        "example": "Nuts, shellfish"
                    }
                }
            },
            "Info": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "example": 1
                    },
                    "title": {
                        "type": "string",
                        "example": "Wedding Schedule"
                    },
                    "content": {
                        "type": "string",
                        "example": "The ceremony starts at 2 PM..."
                    }
                }
            },
            "GalleryMedia": {
                "type": "object",
                "required": ["title", "filename", "media_type"],
                "properties": {
                    "id": {
                        "type": "integer",
                        "example": 1
                    },
                    "title": {
                        "type": "string",
                        "example": "Wedding First Dance"
                    },
                    "description": {
                        "type": "string",
                        "example": "Our first dance as a married couple"
                    },
                    "filename": {
                        "type": "string",
                        "example": "first_dance.jpg"
                    },
                    "media_type": {
                        "type": "string",
                        "enum": ["image", "video", "text"],
                        "example": "image"
                    },
                    "content_type": {
                        "type": "string",
                        "example": "image/jpeg"
                    },
                    "file_size": {
                        "type": "integer",
                        "example": 1024576
                    },
                    "width": {
                        "type": "integer",
                        "example": 1920
                    },
                    "height": {
                        "type": "integer",
                        "example": 1080
                    },
                    "duration": {
                        "type": "number",
                        "format": "float",
                        "example": 60.5,
                        "description": "Video duration in seconds"
                    },
                    "uploaded_by": {
                        "type": "string",
                        "example": "johnmichael"
                    },
                    "upload_time": {
                        "type": "string",
                        "format": "date-time",
                        "example": "2024-12-30T12:00:00Z"
                    },
                    "visibility": {
                        "type": "string",
                        "enum": ["public", "private"],
                        "example": "public"
                    },
                    "likes": {
                        "type": "integer",
                        "example": 42
                    },
                    "tags": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "example": ["dance", "ceremony", "highlights"]
                    },
                    "thumbnail_url": {
                        "type": "string",
                        "example": "thumbnails/first_dance_thumb.jpg"
                    }
                }
            },
            "GalleryComment": {
                "type": "object",
                "required": ["media_id", "comment"],
                "properties": {
                    "id": {
                        "type": "integer",
                        "example": 1
                    },
                    "media_id": {
                        "type": "integer",
                        "example": 1
                    },
                    "user_id": {
                        "type": "integer",
                        "example": 1
                    },
                    "comment": {
                        "type": "string",
                        "example": "Beautiful moment!"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "example": "2024-12-30T12:00:00Z"
                    },
                    "updated_at": {
                        "type": "string",
                        "format": "date-time",
                        "example": "2024-12-30T12:00:00Z"
                    }
                }
            },
            "GalleryAlbum": {
                "type": "object",
                "required": ["title"],
                "properties": {
                    "id": {
                        "type": "integer",
                        "example": 1
                    },
                    "title": {
                        "type": "string",
                        "example": "Wedding Ceremony"
                    },
                    "description": {
                        "type": "string",
                        "example": "Photos from our beautiful ceremony"
                    },
                    "created_by": {
                        "type": "integer",
                        "example": 1
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "example": "2024-12-30T12:00:00Z"
                    },
                    "visibility": {
                        "type": "string",
                        "enum": ["public", "private"],
                        "default": "public",
                        "example": "public"
                    },
                    "cover_image_id": {
                        "type": "integer",
                        "example": 1
                    },
                    "media_items": {
                        "type": "array",
                        "items": {
                            "$ref": "#/definitions/GalleryMedia"
                        }
                    }
                }
            },
            "AlbumMedia": {
                "type": "object",
                "required": ["album_id", "media_id"],
                "properties": {
                    "id": {
                        "type": "integer",
                        "example": 1
                    },
                    "album_id": {
                        "type": "integer",
                        "example": 1
                    },
                    "media_id": {
                        "type": "integer",
                        "example": 1
                    },
                    "position": {
                        "type": "integer",
                        "example": 0
                    },
                    "added_at": {
                        "type": "string",
                        "format": "date-time",
                        "example": "2024-12-30T12:00:00Z"
                    }
                }
            },
            "FAQ": {
                "type": "object",
                "required": ["question", "answer"],
                "properties": {
                    "id": {
                        "type": "integer",
                        "example": 1
                    },
                    "question": {
                        "type": "string",
                        "example": "What time does the ceremony start?"
                    },
                    "answer": {
                        "type": "string",
                        "example": "The ceremony starts at 2 PM sharp."
                    }
                }
            }
        },
        "tags": [
            {
                "name": "Authentication",
                "description": "User authentication endpoints"
            },
            {
                "name": "RSVP",
                "description": "RSVP management endpoints"
            },
            {
                "name": "Information",
                "description": "Wedding information endpoints"
            },
            {
                "name": "Gallery",
                "description": "Photo gallery and media management endpoints"
            },
            {
                "name": "FAQ",
                "description": "Frequently asked questions endpoints"
            }
        ]
    }


    # Swagger configuration
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/swagger/"
    }

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    Swagger(app, template=swagger_template, config=swagger_config)

    @app.route('/')
    def index():
        """
        Landing page
        ---
        responses:
          200:
            description: Welcome message and API status
            schema:
              type: object
              properties:
                message:
                  type: string
                documentation:
                  type: string
                status:
                  type: string
        """
        return jsonify({
            "message": "Welcome to John Michael and Frida's Wedding API",
            "documentation": "/swagger/",
            "status": "operational"
        })

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.rsvp import rsvp_bp
    from app.routes.gallery import gallery_bp
    from app.routes.info import info_bp
    from app.routes.faq import faq_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(rsvp_bp)
    app.register_blueprint(gallery_bp)
    app.register_blueprint(info_bp)
    app.register_blueprint(faq_bp)

    return app