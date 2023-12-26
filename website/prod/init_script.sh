#!/bin/bash

MYSQL_HOST="student-swarm01.maas" 
MYSQL_PORT="3306"
MYSQL_USER="root"
MYSQL_PASSWORD="student"
MYSQL_DATABASE="BE_186044"

SQL_DUMP_FILE="/db_dumb/db.sql"

echo "Creating Database if not exists..." "$MYSQL_DATABASE" < "$SQL_DUMP_FILE"
docker exec -it admin-mysql_db mysql -h"$MYSQL_HOST" -P"$MYSQL_PORT" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS ${MYSQL_DATABASE};"

echo "Applying SQL dump to initialize the database..."
docker exec -i admin-mysql_db mysql -h"$MYSQL_HOST" -P"$MYSQL_PORT" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" < "$SQL_DUMP_FILE"

echo "Initialization complete."
