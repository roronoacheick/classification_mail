import os
import json
import requests


def load_prompt_template(path="prompt.txt"):
    """Load the prompt template from prompt.txt."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def analyze_with_ai(email_body: str) -> dict:
    """
    Analyse un email avec Groq (style OpenAI) et renvoie un dict :
    {
        "category": "...",
        "urgency": "...",
        "summary": "..."
    }
    """

    # Charger le template depuis prompt.txt
    template = load_prompt_template()
    prompt = template.replace("{body}", email_body)

    # Clé API depuis variable d'environnement 
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("Erreur : variable d'environnement GROQ_API_KEY manquante.")

    # Appel API compatible OpenAI
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    # Récupération du texte renvoyé
    content = data["choices"][0]["message"]["content"]

    try:
        # Parse JSON propre
        result = json.loads(content.strip())
    except json.JSONDecodeError:
        # Si l’IA renvoie un truc imparfait → petite sécurité
        raise ValueError("L'IA n'a pas renvoyé un JSON valide :\n" + content)

    return result
