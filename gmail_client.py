import os
import base64
import re
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Permissions demandées : lecture Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_gmail_service():
    """
    Initialise la connexion à l'API Gmail.
    Créé automatiquement le fichier token.json lors du premier lancement.
    """
    creds = None

    # token.json = infos d'authentification sauvegardées (comme dans le corrigé)
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # Si pas de creds ou expirées → lancement du flux OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # credentials.json = ton fichier téléchargé sur Google Cloud
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # On sauvegarde token.json pour les prochaines fois
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Connexion au service Gmail
    service = build('gmail', 'v1', credentials=creds)
    return service


def decode_email_body(msg):
    """
    Décode TOUS les types d’e-mails Gmail :
    - text/plain
    - text/html
    - multipart/alternative
    - multipart/related
    - nested parts
    - emails marketing (MailChimp, LinkedIn, Amazon...)
    """

    def extract_text(payload):
        mime_type = payload.get("mimeType", "")
        body = payload.get("body", {})
        data = body.get("data")

        # Cas simple : text/plain
        if mime_type == "text/plain" and data:
            decoded = base64.urlsafe_b64decode(data)
            return decoded.decode("utf-8", errors="ignore")

        # text/html → nettoyer les balises
        if mime_type == "text/html" and data:
            decoded = base64.urlsafe_b64decode(data)
            html = decoded.decode("utf-8", errors="ignore")
            clean = re.sub("<[^>]+>", "", html)
            return clean

        # Multipart
        if "parts" in payload:
            for part in payload["parts"]:
                result = extract_text(part)
                if result:
                    return result

        return ""

    payload = msg.get("payload", {})

    # BODY direct
    if "data" in payload.get("body", {}):
        decoded = base64.urlsafe_b64decode(payload["body"]["data"])
        try:
            return decoded.decode("utf-8").strip()
        except:
            return decoded.decode("latin-1", errors="ignore").strip()

    # Sinon, chercher dans les parts
    text = extract_text(payload)
    return text.strip()



def fetch_emails(max_results=10):
    """
    Récupère les N derniers e-mails de ta boîte Gmail.
    Retourne une liste propre :
    [
        {"subject": "...", "body": "..."},
        ...
    ]
    """
    service = get_gmail_service()

    # On récupère la liste des messages
    results = service.users().messages().list(
        userId='me', maxResults=max_results
    ).execute()

    messages = results.get('messages', [])

    emails = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me', id=msg['id']
        ).execute()

        # Récupération du sujet
        headers = msg_data['payload']['headers']
        subject = next(
            (h['value'] for h in headers if h['name'] == 'Subject'),
            "(Sans sujet)"
        )

        # Décodage du contenu
        body = decode_email_body(msg_data)

        # Format final utilisé par ton agent IA
        emails.append({
            "subject": subject,
            "body": body
        })

    return emails
