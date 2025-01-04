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



root@2dd0ef532382:/# \dt
bash: dt: command not found
root@2dd0ef532382:/#  \c wedding_db
bash: c: command not found
root@2dd0ef532382:/# psql -U wedding -d wedding_db
psql (15.10 (Debian 15.10-1.pgdg120+1))
Type "help" for help.

wedding_db=# \dt
              List of relations
 Schema |       Name       | Type  |  Owner
--------+------------------+-------+---------
 public | album_media      | table | wedding
 public | alembic_version  | table | wedding
 public | faq              | table | wedding
 public | gallery_albums   | table | wedding
 public | gallery_comments | table | wedding
 public | gallery_media    | table | wedding
 public | info             | table | wedding
 public | rsvps            | table | wedding
 public | users            | table | wedding
(9 rows)

wedding_db=# selectselect * from users
wedding_db-# ;
ERROR:  syntax error at or near "selectselect"
LINE 1: selectselect * from users
        ^
wedding_db=# select * from users
;
wedding_db=# update users set role='admin' where username ='admin';
UPDATE 1
wedding_db=#