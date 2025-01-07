import os

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Database - Bruk Render Postgres URL som default
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',
        'postgresql://wedding2025_db_user:vyYE5tQ6AX8wZ7Yz4WcTsT9VfcdHpx1z@dpg-ctu8901u0jms73f52hs0-a.oregon-postgres.render.com/wedding2025_db'
    )
    
    # Konverter postgres:// til postgresql:// hvis nødvendig
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 60 * 60  # 24 timer
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max filstørrelse
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

    # Debug mode basert på miljø
    DEBUG = os.getenv('FLASK_ENV') == 'development'

class DevelopmentConfig(Config):
    DEBUG = True
    # Ikke overskriv database URI her, bruk den fra Config

class ProductionConfig(Config):
    DEBUG = False
    # Bruk mer sikre verdier i produksjon
    SECRET_KEY = os.getenv('SECRET_KEY', Config.SECRET_KEY)
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', Config.JWT_SECRET_KEY)

def get_config():
    env = os.getenv('FLASK_ENV', 'production')
    if env == 'development':
        return DevelopmentConfig
    return ProductionConfig