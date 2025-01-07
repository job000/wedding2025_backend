import os

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')  # Endre i production
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',
        'postgresql://wedding2025_db_user:vyYE5tQ6AX8wZ7Yz4WcTsT9VfcdHpx1z@dpg-ctu8901u0jms73f52hs0-a.oregon-postgres.render.com/wedding2025_db'
    )
    
    # Ensure we use the correct postgres URL format
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')  # Endre i production
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 60 * 60  # 24 timer
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max filstørrelse
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',
        'postgresql://wedding:password@postgres_db:5432/wedding_db'
    )

class ProductionConfig(Config):
    DEBUG = False
    # Ensure we use environment variables in production
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

# Velg konfigurasjon basert på miljø
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}