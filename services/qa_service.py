# services/qa_service.py
import os
import requests
import json
from dotenv import load_dotenv

# Les imports globaux pour la vérification
try: import google.generativeai as genai
except ImportError: genai = None
try: import openai
except ImportError: openai = None
try: import anthropic
except ImportError: anthropic = None

load_dotenv()
OLLAMA_DEFAULT_MODEL = "codellama:latest"
OLLAMA_HOST = "http://localhost:11434"

class QAService:
    def __init__(self):
        print("Initialisation du QAService...")
        self.genai = genai; self.openai_client = None; self.anthropic_client = None
        if self.genai and os.getenv("GOOGLE_API_KEY"): self.genai.configure(api_key=os.getenv("GOOGLE_API_KEY")); print("Client API Google Gemini configuré.")
        if openai and os.getenv("OPENAI_API_KEY"): self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY")); print("Client API OpenAI configuré.")
        if anthropic and os.getenv("ANTHROPIC_API_KEY"): self.anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")); print("Client API Anthropic configuré.")

    def ask(self, context, question, mode, model_choice):
        print(f"\nRequête 'ask' reçue : mode='{mode}', model_choice='{model_choice}'")
        if mode == "local":
            target_model = OLLAMA_DEFAULT_MODEL if model_choice == "auto" else model_choice
            yield from self._ask_ollama_stream(context, question, target_model)
        elif mode == "api":
            if "gemini" in model_choice: yield from self._ask_gemini_stream(context, question)
            # Les autres API pourraient être ajoutées ici de la même manière
            else: yield from self._ask_gemini_stream(context, question)
        else:
            raise ValueError(f"Mode non supporté : {mode}")

    def _ask_ollama_stream(self, context, question, model_name):
        print(f"--- Requête STREAM à Ollama ({model_name}) ---")
        model_name_lower = model_name.lower()
        prompt = ""
        if not question: # Cas de l'analyse avancée/long doc
            prompt = context
        elif 'phi' in model_name_lower or 'deepseek' in model_name_lower:
            prompt = f"""En te basant sur le document suivant, réponds à ma demande de manière détaillée. Explique ton raisonnement.\n\n**Demande :** {question}\n\n**Document :**\n{context}\n\n**Réponse :**"""
        else:
            prompt = f"Contexte:\n---\n{context}\n---\nBasé UNIQUEMENT sur le contexte, réponds à la question: {question}"
        
        try:
            response = requests.post(url=f"{OLLAMA_HOST}/api/generate", json={"model": model_name, "prompt": prompt, "stream": True}, stream=True, timeout=900)
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    token = chunk.get("response", "")
                    yield token
                    if chunk.get("done"): break
        except Exception as e:
            yield f"\n\n--- ERREUR ---\nErreur de connexion à Ollama : {e}"
            
    def _ask_gemini_stream(self, context, question):
        if not self.genai:
            yield "Erreur: La bibliothèque 'google-generativeai' n'est pas installée."
            return
        print("--- Requête STREAM à l'API Gemini ---")
        prompt = context if not question else f"Contexte:\n---\n{context}\n---\nBasé UNIQUEMENT sur le contexte, réponds à la question: {question}"
        try:
            model = self.genai.GenerativeModel('gemini-1.5-flash')
            # Activer le streaming pour Gemini
            responses = model.generate_content(prompt, stream=True)
            for response in responses:
                if response.parts:
                    yield response.text
        except Exception as e:
            yield f"Erreur avec l'API Gemini : {e}"

qa_service_instance = QAService()