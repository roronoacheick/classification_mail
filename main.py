from ai_client import analyze_with_ai
from gmail_client import fetch_emails

emails = [
    {
        "subject": "Impossible d'accéder au portail RH",
        "body": "Bonjour, le portail RH est indisponible depuis ce matin. Cela bloque toute l'équipe."
    },
    {
        "subject": "Demande d'information pour une facture",
        "body": "Bonjour, j'aimerais obtenir une copie de ma facture du mois dernier. Ce n'est pas urgent."
    },
    {
        "subject": "Bug sur la page d'inscription",
        "body": "Bonjour, un bug empêche les nouveaux utilisateurs de finaliser leur inscription."
    },
    {
        "subject": "Problème de mot de passe",
        "body": "Je ne parviens plus à réinitialiser mon mot de passe, pouvez-vous m'aider ?"
    },
    {
        "subject": "Demande simple",
        "body": "Salut, quand tu peux, j'ai juste besoin d'une info rapide. Pas pressé."
    }
]

sheets_data = {
    "probleme_acces": [],
    "bug_service": [],
    "demande_administrative": [],
    "support_user": []
}

for email in emails:
    # Analyse avec l'IA
    result = analyze_with_ai(email["body"])

    category = result["category"]
    urgency = result["urgency"]
    summary = result["summary"]

    row = [email["subject"], urgency, summary]
    sheets_data[category].append(row)

    print("-------")
    print("Subject:", email["subject"])
    print("Category:", category)
    print("Urgency:", urgency)
    print("Summary:", summary)

print("\n===== Données prêtes pour Google Sheets =====")
for cat, rows in sheets_data.items():
    print(f"\n--- {cat.upper()} ---")
    for r in rows:
        print(r)
