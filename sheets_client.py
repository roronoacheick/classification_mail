from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import os.path
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
def get_sheets_service():
    """
    Initialise et retourne un client Google Sheets.
    Utilise credentials.json et token_sheets.json (séparé de Gmail).
    """

    creds = None  # Pour stocker les identifiants Google une fois récupérés
    token_path = 'token_sheets.json'  # Où l'on sauvegarde le token après autorisation


    # ------------------------------------------------------------------
    # 1) On vérifie si un token existe déjà
    #    → Cela permet d'éviter de ré-autoriser Google à chaque exécution !
    # ------------------------------------------------------------------
    if os.path.exists(token_path):
        # On charge le token existant
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)


    # ------------------------------------------------------------------
    # 2) Si pas de credentials OU credentials expirés, on doit agir
    # ------------------------------------------------------------------
    if not creds or not creds.valid:

        # --------------------------------------
        # 2.1) Si le token est expiré mais renouvelable
        # --------------------------------------
        if creds and creds.expired and creds.refresh_token:
            # Google peut automatiquement rafraîchir l'accès
            creds.refresh(Request())

        else:
            # ----------------------------------------------------------
            # 2.2) Sinon, on doit lancer toute l'authentification Google !
            #      Le navigateur s'ouvrira et demandera ton autorisation.
            # ----------------------------------------------------------
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',  # Ton fichier .json téléchargé sur Google Cloud
                SCOPES
            )
            creds = flow.run_local_server(port=0)  # Ouvre Google dans ton navigateur


        # ------------------------------------------------------------------
        # 3) On sauvegarde le token obtenu dans token_sheets.json
        #    → Pour réutiliser l'accès lors des prochaines exécutions du script
        # ------------------------------------------------------------------
        with open(token_path, 'w') as token:
            token.write(creds.to_json())


    # ------------------------------------------------------------------
    # 4) Création du client Google Sheets
    # ------------------------------------------------------------------
    service = build(
        'sheets',   # API utilisée
        'v4',       # Version de l'API
        credentials=creds  # Identifiants Google
    )

    return service  # On renvoie le client prêt à l'emploi



# ======================================================================
#  FONCTION : write_ticket()
#  Objectif : écrire un ticket dans le bon onglet du Google Sheet.
# ======================================================================
def write_ticket(spreadsheet_id, sheet_name, row_data):
    """
    Ajoute une nouvelle ligne dans l'onglet sheet_name du Google Sheet.
    
    - spreadsheet_id : ID du Google Sheet
    - sheet_name     : Nom de l'onglet (ex : "PROBLEME_ACCES")
    - row_data       : Liste contenant une ligne entière
                       Exemple : ["Sujet", "Urgence", "Résumé"]
    """

    # ------------------------------------------------------------------
    # 1) On obtient un client Google Sheets
    # ------------------------------------------------------------------
    service = get_sheets_service()


    # ------------------------------------------------------------------
    # 2) On définit la zone de destination
    #    → "A1" signifie : commence à la première colonne
    # ------------------------------------------------------------------
    range_ = f"{sheet_name}!A1"


    # ------------------------------------------------------------------
    # 3) Structure des données à envoyer
    # ------------------------------------------------------------------
    body = {
        "values": [row_data]  # row_data est une liste ; on la place dans une liste
    }


    # ------------------------------------------------------------------
    # 4) Requête d'ajout d'une ligne dans Google Sheets
    # ------------------------------------------------------------------
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,  # ID du Sheet
        range=range_,  # Où écrire
        valueInputOption="RAW",  # Écrire le texte brut
        body=body  # Le contenu réel à insérer
    ).execute()


    return result  # Pour debug ou confirmation
