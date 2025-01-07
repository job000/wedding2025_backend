import os

class Config:
    # Flask
    #SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
    SECRET_KEY = 'supersecretkey'  # Hardkodet verdi for lokal utvikling
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
    'DATABASE_URL',
    'postgresql://wedding2025_db_user:password@dpg-ctu8901u0jms73f52hs0-a:5432/wedding2025_db'
)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    #JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwtsecretkey')
    JWT_SECRET_KEY = "jwtsecretkey"

    JWT_ACCESS_TOKEN_EXPIRES = 24 * 60 * 60  # 24 hours