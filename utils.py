# utils.py
import gradio as gr
import pandas as pd
from docx import Document
from wordcloud import WordCloud
from PIL import Image
import spacy

# Chargement du modèle Spacy
try:
    nlp = spacy.load("fr_core_news_sm")
    print("Modèle Spacy 'fr_core_news_sm' chargé dans utils.")
except OSError:
    print("Veuillez installer le modèle Spacy : python -m spacy download fr_core_news_sm")
    nlp = None

def process_text_for_wordcloud(text, synonym_str):
    if nlp is None: raise RuntimeError("Modèle Spacy non chargé.")
    synonym_map = {}
    if synonym_str:
        for line in synonym_str.strip().split('\n'):
            parts = line.split(':')
            if len(parts) == 2:
                target, syns = parts[0].strip(), [s.strip() for s in parts[1].split(',')]
                for s in syns: synonym_map[s.lower()] = target
    doc = nlp(text.lower())
    lemmatized = []
    for token in doc:
        lemma = token.lemma_
        if lemma in synonym_map:
            lemmatized.append(synonym_map[lemma])
        elif token.is_alpha and not token.is_stop and not token.is_punct:
            lemmatized.append(lemma)
    return " ".join(lemmatized)

def generate_advanced_wordcloud(text, synonym_str, colormap):
    if not text or not text.strip():
        gr.Info("Le texte est vide. Impossible de générer un nuage de mots.")
        return None, "Le texte est vide."
    try:
        processed_text = process_text_for_wordcloud(text, synonym_str)
        if not processed_text:
            gr.Info("Le texte ne contient aucun mot pertinent après filtrage.")
            return None, "Aucun mot pertinent trouvé."
        
        wc = WordCloud(width=1200, height=600, background_color='white', colormap=colormap, collocations=False).generate(processed_text)
        return wc.to_image(), "Nuage de mots sémantique généré."
    except Exception as e:
        gr.Error(f"Erreur lors de la génération du nuage de mots : {e}")
        return None, f"Erreur : {e}"

def save_text_to_file(text, file_format, name="export"):
    if not text:
        gr.Warning("Le texte à exporter est vide.")
        return None
    if isinstance(text, str) and text.startswith("<"):
        text = text.replace("<p>", "").replace("</p>", "\n").replace("<br>", "\n")
    try:
        filepath = f"{name}{file_format}"
        if file_format == ".txt":
            with open(filepath, "w", encoding="utf-8") as f: f.write(text)
        elif file_format == ".docx":
            doc = Document()
            doc.add_paragraph(text)
            doc.save(filepath)
        elif file_format == ".csv":
            pd.DataFrame([text], columns=["content"]).to_csv(filepath, index=False, encoding='utf-8-sig')
        gr.Info(f"Fichier exporté : {filepath}")
        return filepath
    except Exception as e:
        gr.Error(f"Erreur lors de la sauvegarde : {e}")
        return None