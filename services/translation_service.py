# services/translation_service.py

import torch
from transformers import pipeline

class TranslationService:
    """
    Gère la traduction de texte entre différentes langues en utilisant NLLB.
    """
    def __init__(self):
        print("Initialisation du Service de Traduction...")
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        print(f"Le service de traduction utilisera le périphérique : {self.device}")

        model_id = "facebook/nllb-200-distilled-600M"
        
        try:
            print(f"Chargement du modèle de traduction '{model_id}'...")
            self.translator = pipeline(
                'translation', 
                model=model_id,
                device=self.device
            )
            print("Modèle de traduction chargé avec succès.")
        except Exception as e:
            print(f"ERREUR critique lors du chargement du modèle de traduction : {e}")
            self.translator = None
    
    def translate(self, text: str, src_lang: str, target_lang: str) -> str:
        """
        Traduit un texte d'une langue source vers une langue cible.
        
        Les codes de langue pour NLLB sont spécifiques. Exemples :
        - Bambara: 'bam_Latn'
        - Peulh (Fula): 'ful_Latn'
        - Français: 'fra_Latn'
        - Anglais: 'eng_Latn'
        """
        if self.translator is None:
            return "Erreur : Le service de traduction n'a pas pu être initialisé."
        
        if not text:
            return ""
            
        print(f"Début de la traduction de '{src_lang}' vers '{target_lang}'...")
        try:
            # NLLB requiert les codes de langue source pour une meilleure performance.
            outputs = self.translator(text, src_lang=src_lang, tgt_lang=target_lang)
            translated_text = outputs[0]['translation_text']
            print("Traduction terminée.")
            return translated_text
        except Exception as e:
            print(f"ERREUR lors de la traduction : {e}")
            return f"Une erreur est survenue pendant la traduction : {e}"

# Instance unique
translation_service_instance = TranslationService()