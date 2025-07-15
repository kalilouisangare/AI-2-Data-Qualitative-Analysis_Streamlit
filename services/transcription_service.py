# services/transcription_service.py

import torch
from transformers import pipeline
import time

class TranscriptionService:
    """
    Gère la transcription de fichiers audio en texte pour le français et l'anglais
    en utilisant le modèle 'whisper-base'.
    """
    def __init__(self):
        print("Initialisation du Service de Transcription (mode simple Fr/En)...")
        
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        print(f"Le service de transcription utilisera le périphérique : {self.device}")

        # Modèle de base, léger et efficace pour les langues à haute ressource.
        model_id = "openai/whisper-base"
        
        try:
            print(f"Chargement du modèle de transcription '{model_id}' depuis le cache...")
            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=model_id,
                device=self.device,
                chunk_length_s=30,
                stride_length_s=5
            )
            print("Modèle de transcription chargé avec succès.")
        except Exception as e:
            print(f"ERREUR critique lors du chargement du modèle de transcription : {e}")
            self.pipe = None

    def transcribe(self, audio_file_path: str, language: str = "auto") -> str:
        """
        Prend le chemin d'un fichier audio et retourne le texte transcrit.
        
        Args:
            audio_file_path (str): Le chemin vers le fichier audio.
            language (str): 'auto' pour la détection, ou un code de langue ('fr', 'en').

        Returns:
            str: Le texte transcrit.
        """
        if self.pipe is None:
            return "Erreur : Le service de transcription n'a pas pu être initialisé."

        print(f"Début de la transcription pour '{audio_file_path}' (Langue spécifiée : {language})")
        start_time = time.time()
        
        # Préparation des paramètres pour le pipeline de transcription
        generate_kwargs = {
            "task": "transcribe"
        }
        # Si une langue est spécifiée (et que ce n'est pas 'auto'), on l'ajoute pour guider le modèle.
        if language and language.lower() != "auto":
            generate_kwargs["language"] = language
            print(f"Forçage de la langue à : {language}")
        else:
            print("Détection automatique de la langue activée.")
            
        try:
            outputs = self.pipe(audio_file_path, generate_kwargs=generate_kwargs)
            transcribed_text = outputs["text"]
            end_time = time.time()
            print(f"Transcription terminée en {end_time - start_time:.2f} secondes.")
            return transcribed_text.strip()
        except Exception as e:
            print(f"ERREUR lors de la transcription : {e}")
            return f"Une erreur est survenue pendant la transcription : {e}"

# Création de l'instance unique du service qui sera utilisée par le reste de l'application.
transcription_service_instance = TranscriptionService()