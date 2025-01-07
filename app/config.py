import os

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
    
    # Database - Sjekk om vi er på Render
    if os.getenv('RENDER'):
        SQLALCHEMY_DATABASE_URI = (
            'postgresql://wedding2025_db_user:vyYE5tQ6AX8wZ7Yz4WcTsT9VfcdHpx1z@'
            'dpg-ctu8901u0jms73f52hs0-a.oregon-postgres.render.com/wedding2025_db'
        )
    else:
        # Lokal database konfigurasjon
        SQLALCHEMY_DATABASE_URI = os.getenv(
            'DATABASE_URL',
            'postgresql://wedding:password@postgres_db:5432/wedding_db'
        )
    
    # Konverter postgres:// til postgresql:// hvis nødvendig
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT konfigurasjon
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwtsecretkey')
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 60 * 60  # 24 hours
    
    # CORS konfigurasjon
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # File Upload konfigurasjon
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max filstørrelse
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    
    # Debug modus
    DEBUG = not os.getenv('RENDER')