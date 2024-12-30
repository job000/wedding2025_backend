# 1. Stopp alle containere og fjern volumer
docker-compose down -v

# 2. Start postgres først og vent på at den er klar
docker-compose up -d postgres_db
sleep 10  # Vent 10 sekunder for å være sikker på at postgres er oppe

# 3. Start flask-appen
docker-compose up -d flask_app

# 4. Initialiser databasen og kjør migreringer
docker-compose exec flask_app flask db init
docker-compose exec flask_app flask db migrate -m "initial migration"
docker-compose exec flask_app flask db upgrade

# 5. Sjekk loggene
docker-compose logs -f