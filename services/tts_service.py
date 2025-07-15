# services/tts_service.py

import torch
from transformers import pipeline
import soundfile as sf

class TTSService:
    """
    Gère la conversion de texte en parole. Charge le modèle à la demande pour économiser la VRAM.
    """
    def __init__(self):
        print("Service TTS initialisé (modèle non chargé).")
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.model_id = "suno/bark-small"
        self.pipe = None
    
    def synthesize(self, text: str, output_path: str):
        """
        Génère un fichier audio. Le modèle est chargé pour cette tâche puis déchargé.
        """
        try:
            if self.pipe is None:
                print(f"Chargement à la demande du modèle TTS '{self.model_id}' sur {self.device}...")
                self.pipe = pipeline("text-to-speech", self.model_id, device=self.device)

            print("Synthèse vocale en cours...")
            # Limite le texte pour éviter les erreurs avec le modèle Bark
            speech = self.pipe(text[:1000]) 
            sf.write(output_path, speech["audio"], samplerate=speech["sampling_rate"])
            print("Fichier audio généré avec succès.")
        
        except Exception as e:
            print(f"ERREUR dans le service TTS : {e}")
            raise e
            
        finally:
            if self.pipe is not None:
                print("Déchargement du modèle TTS...")
                self.pipe = None
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

tts_service_instance = TTSService()