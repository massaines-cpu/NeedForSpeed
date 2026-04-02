#!/bin/bash

echo "=== Lancement du jeu de voitures ==="

# Lance un serveur HTTP pour servir index.html sur le port 3000
# python3 -m http.server est inclus dans Python, pas besoin de l'installer
echo "Lancement du serveur HTML sur http://localhost:3000 ..."
python3 -m http.server 3000 &

# Lance l'API FastAPI sur le port 8000
echo "Lancement de l'API FastAPI sur http://localhost:8000 ..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &

echo ""
echo "Tout est lancé !"
echo "Ouvre http://localhost:3000 dans ton navigateur"
echo ""
echo "Pour arrêter tout : appuie sur Ctrl+C"

# Attend que tu appuies sur Ctrl+C, puis tue les deux processus
trap "echo 'Arrêt...'; kill 0" EXIT
wait