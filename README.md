# Jeu de voitures

Petit jeu multijoueur en temps réel avec FastAPI (Python) et HTML/CSS/JS.

## Ce que fait le projet

- Un joueur entre son pseudo
- Il choisit 4 instructions (Avancer, Tourner gauche, Tourner droite)
- Quand tous les joueurs ont envoyé leurs instructions, les voitures bougent
- Tout le monde voit les voitures se déplacer en temps réel

## Installation

### 1. Cloner ou télécharger le projet

### 2. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 3. Lancer l'API

```bash
uvicorn main:app --reload
```

L'API tourne sur `http://127.0.0.1:8000`

### 4. Ouvrir le front

Ouvre le fichier `index.html` dans ton navigateur.
(ou avec l'extension **Live Server** dans VS Code)

## Structure du projet

```
├── main.py           # API FastAPI (back-end)
├── index.html        # Interface (front-end)
├── requirements.txt  # Dépendances Python
└── README.md         # Ce fichier
```

## Routes de l'API

| Méthode | Route    | Description                        |
|---------|----------|------------------------------------|
| GET     | /ping    | Vérifie que l'API fonctionne       |
| POST    | /pseudo  | Enregistre un nouveau joueur       |
| WS      | /ws      | Connexion WebSocket temps réel     |

## Messages WebSocket

Le front envoie deux types de messages JSON :

**Identification** (après connexion) :
```json
{ "type": "identification", "pseudo": "Alice" }
```

**Instructions** (4 actions choisies) :
```json
{ "type": "instructions", "pseudo": "Alice", "instructions": ["A", "B", "A", "C"] }
```

- `A` = Avancer
- `B` = Tourner à gauche
- `C` = Tourner à droite