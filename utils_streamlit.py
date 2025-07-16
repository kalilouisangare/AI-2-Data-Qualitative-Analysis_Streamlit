# utils_streamlit.py
import streamlit as st
import pandas as pd
from docx import Document
from wordcloud import WordCloud
import spacy
import io

# --- CONFIGURATION ---
# Chargement du modèle Spacy en utilisant le cache de Streamlit pour la performance
@st.cache_resource
def load_spacy_model():
    try:
        nlp = spacy.load("fr_core_news_sm")
        print("Modèle Spacy 'fr_core_news_sm' chargé.")
        return nlp
    except OSError:
        st.error("Le modèle Spacy 'fr_core_news_sm' n'est pas installé.")
        st.code("python -m spacy download fr_core_news_sm")
        return None

nlp = load_spacy_model()

# --- FONCTIONS DE TRAITEMENT DE TEXTE ---

def process_text_for_wordcloud(text, synonym_str):
    """Traite le texte pour le nuage de mots : lemmatisation et gestion des synonymes."""
    if nlp is None:
        st.error("Le modèle Spacy n'est pas chargé, impossible de générer le nuage de mots.")
        raise RuntimeError("Modèle Spacy non chargé.")

    synonym_map = {}
    if synonym_str:
        for line in synonym_str.strip().split('\n'):
            parts = line.split(':')
            if len(parts) == 2:
                target, syns = parts[0].strip(), [s.strip() for s in parts[1].split(',')]
                for s in syns:
                    synonym_map[s.lower()] = target.lower()

    doc = nlp(text.lower())
    lemmatized_words = []
    for token in doc:
        # On utilise la forme lemmatisée comme clé pour la recherche de synonymes
        lemma = token.lemma_.lower()
        if lemma in synonym_map:
            lemmatized_words.append(synonym_map[lemma])
        # On garde les mots qui sont alphabétiques, pas des mots vides (stop words) et pas de la ponctuation
        elif token.is_alpha and not token.is_stop and not token.is_punct:
            lemmatized_words.append(lemma)
            
    return " ".join(lemmatized_words)

def generate_advanced_wordcloud(text, synonym_str, colormap):
    """Génère et retourne une image de nuage de mots."""
    if not text or not text.strip():
        st.info("Le texte est vide. Impossible de générer un nuage de mots.")
        return None, "Le texte est vide."
    try:
        processed_text = process_text_for_wordcloud(text, synonym_str)
        if not processed_text.strip():
            st.info("Le texte ne contient aucun mot pertinent après le filtrage.")
            return None, "Aucun mot pertinent trouvé."
        
        wc = WordCloud(
            width=1200,
            height=600,
            background_color='white',
            colormap=colormap,
            collocations=False
        ).generate(processed_text)
        
        return wc.to_image(), "Nuage de mots sémantique généré avec succès."
    except Exception as e:
        st.error(f"Erreur lors de la génération du nuage de mots : {e}")
        return None, f"Erreur : {e}"

# --- FONCTIONS D'EXPORTATION ---

def get_download_data(text, file_format, name="export"):
    """
    Prépare les données pour le bouton de téléchargement de Streamlit.
    Retourne les données en bytes, le nom du fichier et le type MIME.
    """
    if not text:
        st.warning("Le texte à exporter est vide.")
        return None, None, None

    # Nettoyage simple du HTML potentiel
    if isinstance(text, str) and text.startswith("<"):
        text = text.replace("<p>", "").replace("</p>", "\n").replace("<br>", "\n")

    file_name = f"{name}{file_format}"
    
    try:
        if file_format == ".txt":
            data = text.encode("utf-8")
            mime = "text/plain"
        elif file_format == ".docx":
            doc = Document()
            doc.add_paragraph(text)
            bio = io.BytesIO()
            doc.save(bio)
            data = bio.getvalue()
            mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif file_format == ".csv":
            # Crée un buffer en mémoire pour le CSV
            output = io.StringIO()
            pd.DataFrame([text], columns=["content"]).to_csv(output, index=False, encoding='utf-8-sig')
            data = output.getvalue().encode("utf-8")
            mime = "text/csv"
        else:
            # Si le format n'est pas reconnu, on ne retourne rien
            return None, None, None

        return data, file_name, mime
    except Exception as e:
        st.error(f"Erreur lors de la préparation du fichier pour le téléchargement : {e}")
        return None, None, None