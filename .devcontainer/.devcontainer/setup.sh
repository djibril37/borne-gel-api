#!/bin/bash

echo "🚀 Configuration du projet Borne Gel API..."

# Installer MySQL
sudo apt update
sudo apt install -y mysql-server mysql-client

# Démarrer MySQL
sudo service mysql start

# Créer la base de données et l'utilisateur
sudo mysql -e "CREATE DATABASE IF NOT EXISTS borne_gel_db;"
sudo mysql -e "CREATE USER IF NOT EXISTS 'api_user'@'localhost' IDENTIFIED BY 'apipassword';"
sudo mysql -e "GRANT ALL PRIVILEGES ON borne_gel_db.* TO 'api_user'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

# Installer les dépendances Python
pip install -r requirements.txt

echo "✅ Installation terminée !"
echo "👉 Pour démarrer l'API : uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"