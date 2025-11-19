# ======================================================================
#  main.py – Pipeline complet :
#  1. Lire les emails Gmail
#  2. Nettoyer le contenu des mails
#  3. Analyser avec l'IA (Groq)
#  4. Déterminer la catégorie + urgence + synthèse
#  5. Envoyer dans Google Sheets
# ======================================================================


# ----------------------------------------------------------------------
#  IMPORTS DU PROJET
# ----------------------------------------------------------------------

# Fonction IA (analyse du mail)
from ai_client import analyze_with_ai

# Fonction pour récupérer les emails Gmail
from gmail_client import fetch_emails

# Fonction pour écrire dans Google Sheets
from sheets_client import write_ticket


# ----------------------------------------------------------------------
#  ID DU GOOGLE SHEET
#  Très important : remplace par TON vrai ID de Sheet !
# ----------------------------------------------------------------------
SPREADSHEET_ID = "1c_IjWLggb370DnbIr5F0s57FXzV1NOV9psNZm1ox0DE"



# ======================================================================
#  FONCTION : Nettoyer légèrement le body avant de l'envoyer à l'IA
#  Objectif : éviter d'envoyer des mails immenses avec 40 liens,
#             réduire le bruit pour que l’IA analyse mieux.
# ======================================================================
import re

def clean_body_for_ai(body: str) -> str:
    """
    Nettoie le texte :
    - retire les URLs trop longues
    - enlève les lignes vides multiples
    - coupe si le mail dépasse 800 caractères
    """
    
    # 1) Remplacer toutes les URLs par un token [URL]
    body = re.sub(r"https?://\S+", "[URL]", body)

    # 2) Réduire les lignes vides
    body = re.sub(r"\n\s*\n", "\n", body)

    # 3) Limiter la taille pour l'IA
    if len(body) > 800:
        body = body[:800] + "\n[...]"

    return body.strip()



# ======================================================================
#  CORRESPONDANCE catégorie → nom d'onglet Google Sheets
# ======================================================================
sheet_map = {
    "probleme_acces": "PROBLEME_ACCES",
    "bug_service": "BUG_SERVICE",
    "demande_administrative": "DEMANDE_ADMIN",
    "support_user": "SUPPORT_USER",
    "autre": "AUTRE"
}



# ======================================================================
#  FONCTION PRINCIPALE
# ======================================================================
def main():

    print("\n===== Lecture des emails Gmail =====\n")

    # ------------------------------------------------------------------
    # 1) Récupérer les emails Gmail (ex : les 5 derniers)
    # ------------------------------------------------------------------
    emails = fetch_emails(max_results=5)

    print(f"{len(emails)} emails récupérés.\n")


    # ------------------------------------------------------------------
    # 2) Traiter chaque email un par un
    # ------------------------------------------------------------------
    for email in emails:

        print("--------------------------------------------------")
        print("Sujet :", email["subject"])

        # A → On nettoie un peu le body
        cleaned_body = clean_body_for_ai(email["body"])

        print("\nAnalyse IA en cours...\n")

        # B → On envoie le texte nettoyé à l’IA Groq
        result = analyze_with_ai(cleaned_body)

        # C → On extrait les données du JSON renvoyé
        category = result["category"]
        urgency = result["urgency"]
        summary = result["summary"]

        print("Catégorie IA      :", category)
        print("Niveau d'urgence  :", urgency)
        print("Résumé IA         :", summary)


        # ------------------------------------------------------------------
        # 3) Déterminer l’onglet du Google Sheet
        # ------------------------------------------------------------------
        sheet_name = sheet_map.get(category, "AUTRE")

        print(f"Écriture dans la feuille : {sheet_name}")


        # ------------------------------------------------------------------
        # 4) Préparer la ligne à écrire
        # ------------------------------------------------------------------
        row = [
            email["subject"],
            urgency,
            summary
        ]


        # ------------------------------------------------------------------
        # 5) Envoyer dans Google Sheets
        # ------------------------------------------------------------------
        write_ticket(
            SPREADSHEET_ID,
            sheet_name,
            row
        )

        print("✔ Ticket ajouté au Google Sheet\n")


    print("\n===== Pipeline complet exécuté avec succès ! =====\n")



# ======================================================================
#  Lancer le programme
# ======================================================================
if __name__ == "__main__":
    main()
