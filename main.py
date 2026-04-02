import fastapi
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket, WebSocketDisconnect

app = fastapi.FastAPI()

# Autoriser le front (HTML/JS) à parler à l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------
# STRUCTURE D'UN UTILISATEUR
# ---------------------------------------------------
# On stocke tous les utilisateurs connectés dans ce tableau
# Chaque utilisateur est un dict avec :
#   - pseudo     : son nom
#   - socket     : sa connexion WebSocket (pour lui envoyer des messages)
#   - position   : {"x": int, "y": int}
#   - direction  : "haut" | "bas" | "gauche" | "droite"
#   - instructions: [] ou ["A","B","C","A"] (liste de 4 instructions)

utilisateurs: list[dict] = []


# ---------------------------------------------------
# ROUTE 1 : /ping  (test que l'API fonctionne)
# ---------------------------------------------------
@app.get("/ping")
def ping():
    return {"message": "pong"}


# ---------------------------------------------------
# ROUTE 2 : /pseudo  (ajouter un utilisateur)
# La connexion WebSocket se fait juste après dans /ws
# On stocke juste le pseudo ici pour l'instant,
# le socket sera ajouté quand il se connecte au /ws
# ---------------------------------------------------
@app.post("/pseudo")
def ajouter_pseudo(body: dict):
    pseudo = body.get("pseudo", "Anonyme")
    # On vérifie que ce pseudo n'est pas déjà pris
    for u in utilisateurs:
        if u["pseudo"] == pseudo:
            return {"message": f"pseudo '{pseudo}' déjà pris"}
    # On crée l'utilisateur (sans socket pour l'instant)
    utilisateurs.append({
        "pseudo": pseudo,
        "socket": None,
        "position": {"x": 0, "y": 0},
        "direction": "haut",
        "instructions": []
    })
    return {"message": f"pseudo '{pseudo}' enregistré"}


# ---------------------------------------------------
# FONCTION UTILITAIRE : envoyer la liste des users
# à tous les clients connectés (sans le socket)
# ---------------------------------------------------
async def broadcast_utilisateurs():
    # On prépare la liste sans le socket (pas sérialisable en JSON)
    liste_publique = [
        {
            "pseudo": u["pseudo"],
            "position": u["position"],
            "direction": u["direction"],
            "instructions": u["instructions"]
        }
        for u in utilisateurs if u["socket"] is not None
    ]
    # On envoie à tout le monde
    for u in utilisateurs:
        if u["socket"] is not None:
            await u["socket"].send_json({"type": "liste_utilisateurs", "data": liste_publique})


# ---------------------------------------------------
# FONCTION : calculer la nouvelle position d'une voiture
# selon ses 4 instructions (A = avancer, B = gauche, C = droite)
# ---------------------------------------------------
def calculer_nouvelle_position(user: dict):
    # Ordre des directions pour tourner (dans le sens horaire)
    ordre_directions = ["haut", "droite", "bas", "gauche"]

    position = dict(user["position"])  # copie
    direction = user["direction"]

    for instruction in user["instructions"]:
        if instruction == "B":  # Tourner à gauche
            index = ordre_directions.index(direction)
            direction = ordre_directions[(index - 1) % 4]

        elif instruction == "C":  # Tourner à droite
            index = ordre_directions.index(direction)
            direction = ordre_directions[(index + 1) % 4]

        elif instruction == "A":  # Avancer d'une case
            if direction == "haut":
                position["y"] -= 1
            elif direction == "bas":
                position["y"] += 1
            elif instruction == "gauche":
                position["x"] -= 1
            elif direction == "droite":
                position["x"] += 1

    user["position"] = position
    user["direction"] = direction
    user["instructions"] = []  # On remet à zéro après calcul


# ---------------------------------------------------
# ROUTE 3 : /ws  (WebSocket)
# Le client s'y connecte après avoir entré son pseudo
# ---------------------------------------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    pseudo_connecte = None  # On ne sait pas encore qui c'est

    try:
        while True:
            # On attend un message JSON du client
            data = await websocket.receive_json()

            # --- Le client s'identifie ---
            # Message attendu : {"type": "identification", "pseudo": "Alice"}
            if data["type"] == "identification":
                pseudo_connecte = data["pseudo"]
                # On retrouve cet utilisateur dans la liste et on lui attache le socket
                for u in utilisateurs:
                    if u["pseudo"] == pseudo_connecte:
                        u["socket"] = websocket
                        break
                # On envoie la liste de tous les connectés à tout le monde
                await broadcast_utilisateurs()

            # --- Le client envoie ses 4 instructions ---
            # Message attendu : {"type": "instructions", "pseudo": "Alice", "instructions": ["A","B","A","C"]}
            elif data["type"] == "instructions":
                pseudo_connecte = data["pseudo"]
                # On stocke ses instructions
                for u in utilisateurs:
                    if u["pseudo"] == pseudo_connecte:
                        u["instructions"] = data["instructions"]
                        break

                # On vérifie si TOUS les joueurs connectés ont envoyé leurs instructions
                tous_prets = all(
                    len(u["instructions"]) == 4
                    for u in utilisateurs if u["socket"] is not None
                )

                if tous_prets:
                    # On envoie d'abord l'état actuel (avec les instructions visibles)
                    await broadcast_utilisateurs()
                    # Puis on calcule les nouvelles positions
                    for u in utilisateurs:
                        if u["socket"] is not None:
                            calculer_nouvelle_position(u)
                    # Et on renvoie l'état mis à jour
                    await broadcast_utilisateurs()

    except WebSocketDisconnect:
        # Le client s'est déconnecté : on retire son socket
        for u in utilisateurs:
            if u["pseudo"] == pseudo_connecte:
                u["socket"] = None
                break
        await broadcast_utilisateurs()