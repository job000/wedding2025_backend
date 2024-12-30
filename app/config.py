import os

class Config:
    # Flask
    #SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
    SECRET_KEY = 'supersecretkey'  # Hardkodet verdi for lokal utvikling
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://wedding:password@postgres_db:5432/wedding_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    #JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwtsecretkey')
    JWT_SECRET_KEY = "supersecretkey"

    JWT_ACCESS_TOKEN_EXPIRES = 24 * 60 * 60  # 24 hours