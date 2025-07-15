# services/summarization_service.py

import torch
from transformers import pipeline
import os

class SummarizationService:
    """
    Gère la génération de résumés de texte en utilisant un modèle pré-entraîné.
    Inclut des optimisations pour améliorer la qualité de la génération.
    """
    def __init__(self):
        print("Initialisation du Service de Résumé...")
        
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        print(f"Le service de résumé utilisera le périphérique : {self.device}")

        # Le nom d'identification du modèle sur le Hub de Hugging Face.
        model_id = "airKlizz/mt5-base-wikinewssum-french"
        
        try:
            print(f"Chargement du modèle de résumé '{model_id}' depuis le cache...")
            self.summarizer = pipeline(
                "summarization",
                model=model_id,
                device=self.device
            )
            print("Modèle de résumé chargé avec succès.")
        except Exception as e:
            print(f"ERREUR critique lors du chargement du modèle de résumé : {e}")
            self.summarizer = None
            
    def summarize(self, text: str, min_length: int = 30, max_length: int = 150) -> str:
        """
        Génère un résumé pour le texte fourni.
        Les valeurs de min_length et max_length sont celles reçues de l'interface.
        Les valeurs '30' et '150' ne sont que des valeurs par défaut.

        Args:
            text (str): Le texte à résumer.
            min_length (int): La longueur minimale du résumé généré.
            max_length (int): La longueur maximale du résumé généré.

        Returns:
            str: Le texte résumé.
        """
        if self.summarizer is None:
            return "Erreur : Le service de résumé n'est pas initialisé. Vérifiez les logs pour les erreurs de chargement."
        if not text:
            return "Le texte fourni est vide."
        
        print(f"Début du résumé (longueur min:{min_length}, max:{max_length})...")
        
        # Ajout d'un préfixe pour guider le modèle T5.
        text_with_prefix = "résume ce texte: " + text
        
        try:
            result = self.summarizer(
                text_with_prefix,
                min_length=min_length,       # Utilise la valeur reçue de l'interface
                max_length=max_length,       # Utilise la valeur reçue de l'interface
                no_repeat_ngram_size=3,
                num_beams=4,
                early_stopping=True
            )
            
            summary = result[0]['summary_text']
            print("Résumé terminé.")
            return summary
            
        except Exception as e:
            print(f"ERREUR lors du résumé : {e}")
            return f"Une erreur est survenue pendant le résumé : {e}"

# Création de l'instance unique du service.
summarization_service_instance = SummarizationService()