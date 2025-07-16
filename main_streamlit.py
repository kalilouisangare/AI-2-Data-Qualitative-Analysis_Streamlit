# main_streamlit.py
import streamlit as st
import requests
import os
from dotenv import load_dotenv
from utils_streamlit import generate_advanced_wordcloud, get_download_data

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Outil d'Analyse Qualitative",
    page_icon="assets/logo.png",
    layout="wide"
)

# --- CONFIGURATION AU DÉMARRAGE ---
load_dotenv()

# Modèles disponibles (similaire à la version Gradio)
MODELS_STANDARD = ["auto", "codellama:latest", "llava:latest"]
MODELS_REASONING = ["phi4-mini-reasoning:latest", "deepseek-r1:8b"]
MODELS_API = [os.getenv("GEMINI_MODEL_NAME", "gemini-flash")] if os.getenv("GOOGLE_API_KEY") else ["api_non_configuree"]

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# --- INITIALISATION DE L'ÉTAT DE SESSION ---
def init_session_state():
    if 'context' not in st.session_state:
        st.session_state.context = ""
    if 'is_audio' not in st.session_state:
        st.session_state.is_audio = False
    if 'upload_status' not in st.session_state:
        st.session_state.upload_status = ""
    if 'summary' not in st.session_state:
        st.session_state.summary = ""
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Accueil"

init_session_state()

# --- FONCTIONS DE COMMUNICATION AVEC LE BACKEND ---

def upload_file_to_backend(uploaded_file, language):
    if uploaded_file is not None:
        files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        data = {'language': language}
        try:
            with st.spinner("Traitement du fichier en cours..."):
                response = requests.post(f"{BACKEND_URL}/upload-file/", files=files, data=data)
                response.raise_for_status()
                result = response.json()
                st.session_state.context = result.get("full_text", "")
                st.session_state.is_audio = result.get("is_audio", False)
                st.session_state.upload_status = result.get("message", "Erreur lors du traitement.")
                st.session_state.summary = "" # Réinitialiser le résumé lors d'un nouveau chargement
                st.session_state.active_tab = "Analyse"
                st.success("Fichier traité avec succès !")
        except requests.exceptions.RequestException as e:
            st.error(f"Erreur de communication avec le backend : {e}")

def summarize_context(context, is_audio, min_len, max_len):
    """Appelle le backend pour générer un résumé."""
    if not context or not is_audio:
        st.warning("Le résumé n'est disponible que pour les fichiers audio chargés.")
        return
    
    payload = {"context": context, "is_audio": is_audio, "min_length": min_len, "max_length": max_len}
    try:
        with st.spinner("Génération du résumé en cours..."):
            response = requests.post(f"{BACKEND_URL}/summarize-context/", data=payload)
            response.raise_for_status()
            result = response.json()
            if "summary" in result:
                st.session_state.summary = result["summary"]
                st.success("Résumé généré !")
            else:
                st.error(result.get("message", "Erreur inconnue lors du résumé."))
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de communication avec le backend : {e}")

def stream_llm_response(endpoint: str, payload: dict):
    """Fonction pour streamer la réponse du backend et l'afficher dans Streamlit."""
    try:
        with requests.post(endpoint, data=payload, stream=True, timeout=900) as response:
            response.raise_for_status()
            st.write_stream(response.iter_content(chunk_size=None, decode_unicode=True))
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de communication avec le LLM : {e}")

# --- INTERFACE UTILISATEUR ---

with st.sidebar:
    st.image("assets/logo.png", width=100)
    st.title("Chargement des Données")
    
    uploaded_file = st.file_uploader(
        "Chargez un document", 
        type=['pdf', 'docx', 'txt', 'csv', 'xlsx', 'xls', 'mp3', 'wav', 'm4a', 'flac', 'ogg']
    )
    lang_options = {"Auto-détection": "auto", "Français": "fr", "Anglais": "en"}
    selected_lang = st.selectbox("Langue de l'audio (si applicable)", options=list(lang_options.keys()))

    if st.button("Analyser le document", type="primary"):
        if uploaded_file:
            upload_file_to_backend(uploaded_file, lang_options[selected_lang])
        else:
            st.warning("Veuillez d'abord sélectionner un fichier.")

    if st.session_state.upload_status:
        st.info(st.session_state.upload_status)

tab_titles = ["Accueil", "Guide", "Analyse", "Visualisation"]
accueil_tab, guide_tab, analyse_tab, viz_tab = st.tabs(tab_titles)

with accueil_tab:
    st.title("Outil d'Analyse Qualitative Intelligente")
    st.markdown(
        '''
        ## Donnez à vos Données une Voix Intelligente
        Bienvenue sur la plateforme d'analyse de données qualitatives. Cet outil est conçu pour transformer vos documents et entretiens en informations exploitables, en combinant la puissance des modèles de langage de pointe avec une interface intuitive, le tout en garantissant une confidentialité totale grâce à une exécution 100% locale.
        Cela a ete rendu possible par M. Kalilou I Sangare, un professionnel expérimenté avec plus de 8 années du Suivi-Evaluation-Apprentissage-Redevabilité et Data Scientiste avec l'appui technique de l'IA Générative de Google Gemini 2.5 Pro
        
    
        ---
        ### L'Intelligence Artificielle au service de l'Analyse
        Le traitement des données qualitatives – transcriptions d'entretiens, réponses ouvertes, rapports – est traditionnellement un processus long et subjectif. Ce projet propose de le révolutionner en automatisant les tâches ardues. Grâce aux modèles de langage (LLM), nous pouvons comprendre les nuances, identifier les thèmes émergents et synthétiser des concepts complexes.
        
        ### De la Donnée Brute à la Décision
        Notre outil facilite la transition de la donnée brute à la décision éclairée. Un rapport de 100 pages peut être résumé en quelques minutes via la fonction d'analyse de longs documents. Les réponses de centaines de personnes à une enquête peuvent être analysées pour en faire ressortir les tendances principales.
        
        ### Une Boîte à Outils Complète et Locale
        La plateforme orchestre différents modèles d'IA spécialisés. Un modèle de transcription convertit la parole en texte. Un modèle de résumé synthétise les points clés. Enfin, des LLM généralistes ou de raisonnement permettent une interrogation flexible des données, le tout sur votre machine, assurant que vos données sensibles restent confidentielles.
        
        ### Flexibilité et Puissance
        Que vous ayez besoin d'une réponse rapide à une question simple, d'un résumé automatique, ou d'une analyse en profondeur avec un raisonnement détaillé, l'outil s'adapte à vos besoins.
        
        ### Comment ça marche  ?
        Naviguez et suivez simplement le guide d'utilisation qui vous expliquera pour chaque niveau à travers les différents onglets ci-dessus.
        '''
    )

with guide_tab:
    st.header("Guide d'Utilisation")
    st.markdown(
        '''
        ## Guide d'Utilisation de l'Outil
        
        ### Étape 1 : Charger vos Données
        C'est le point de départ. Uploadez n'importe quel fichier (`.pdf`, `.docx`, `.txt`, `.csv`, `.mp3`, `.wav`). Le contenu sera extrait et affiché. Après le chargement, vous serez automatiquement redirigé vers l'onglet **"Étape 2 : Analyser le Contenu"**.
        
        ### Étape 2 : Analyser le Contenu
        - **2.1 Résumé Automatique (Audio Uniquement) :** Cet onglet n'est visible qu'après avoir chargé un fichier audio. Il utilise un modèle spécialisé pour créer un résumé concis.
        - **2.2 Interrogation Standard (Q&A) :** Parfait pour poser des questions directes et factuelles. Ex: *"Quels sont les 3 principaux défis mentionnés ?"*.
        - **2.3 Analyse par Raisonnement :** Pour les questions ouvertes et complexes. Ex: *"Analyse les forces et faiblesses du projet."*. Les modèles comme `phi4-mini-reasoning` sont conçus pour "penser" à voix haute et montrer leur processus de déduction.
        - **2.4 Analyse de Long Document :** Indispensable pour les documents de plus de 10-20 pages. L'outil découpe le texte, l'analyse par morceaux, et synthétise le tout en une réponse finale cohérente.
        
        ### Étape 3 : Visualiser les Données
        - **Nuage de Mots Sémantique :** Cet outil va au-delà du simple comptage. Il regroupe les mots par leur racine (ex: *analyse, analyser, analysé* deviennent *analyse*) et vous permet de définir vos propres regroupements de synonymes pour faire ressortir les concepts clés.
            - **Format des synonymes :** `mot_cible: synonyme1, synonyme2` (un par ligne).
            - **Exemple :** `satisfaction: content, heureux, joie`
        '''
    )

with analyse_tab:
    st.header("Analyse du Contenu")
    if not st.session_state.context:
        st.info("Veuillez charger un document via la barre latérale pour commencer l'analyse.")
    else:
        st.text_area("Contexte / Transcription (extrait)", st.session_state.context[:2000], height=200, disabled=True)

        analysis_tabs = st.tabs(["Résumé (Audio)", "Interrogation (Q&A)", "Analyse de Long Document"])

        with analysis_tabs[0]:
            st.subheader("Résumé Automatique (pour fichiers audio)")
            if not st.session_state.is_audio:
                st.warning("Cette fonctionnalité est uniquement activée pour les fichiers audio.")
            else:
                min_len = st.slider("Longueur minimale du résumé", 5, 100, 20)
                max_len = st.slider("Longueur maximale du résumé", 50, 512, 120)
                if st.button("Générer le résumé"):
                    with st.spinner("Analyse en cours, veuillez patienter..."):
                        summarize_context(st.session_state.context, st.session_state.is_audio, min_len, max_len)
                
                if st.session_state.summary:
                    st.text_area("Résultat du Résumé", st.session_state.summary, height=250)

        with analysis_tabs[1]:
            st.subheader("Interrogation Standard (Q&A)")
            st.markdown("Posez des questions directes aux LLM standards.")
            
            qa_mode = st.radio("Mode", ["local", "api"], key="qa_mode", horizontal=True)
            
            if qa_mode == 'local':
                model_selector = st.selectbox("Modèle Standard", MODELS_STANDARD, key="qa_model")
            else:
                model_selector = st.selectbox("Modèle API", MODELS_API, key="qa_model_api")

            question_box = st.text_area("Posez votre question ici", height=100, placeholder="Ex: Quels sont les points clés ?")

            if st.button("Obtenir une Réponse", key="qa_submit"):
                if question_box:
                    model_choice = model_selector
                    if qa_mode == "api":
                        model_choice = MODELS_API[0] if MODELS_API else "api_non_configuree"
                    
                    payload = {
                        "question": question_box, 
                        "context": st.session_state.context, 
                        "mode": qa_mode, 
                        "model_choice": model_choice
                    }
                    st.markdown("### Réponse du Modèle")
                    with st.spinner("Analyse en cours, veuillez patienter..."):
                        with st.container(height=400, border=True):
                            stream_llm_response(f"{BACKEND_URL}/ask-question/", payload)
                else:
                    st.warning("Veuillez poser une question.")

        with analysis_tabs[2]:
            st.subheader("Analyse de Long Document")
            st.markdown("Analysez des documents volumineux. Le mode API est recommandé pour sa rapidité.")

            long_doc_mode = st.radio("Mode", ["local", "api"], key="long_doc_mode", horizontal=True)

            if long_doc_mode == 'local':
                long_doc_model_selector = st.selectbox("Modèle", MODELS_STANDARD, index=1, key="long_doc_model")
            else:
                long_doc_model_selector = st.selectbox("Modèle API", MODELS_API, key="long_doc_model_api")

            analysis_type_dropdown = st.selectbox(
                "Type d'Analyse Prédéfinie",
                options=[("Synthèse Générale", "resume_general"), ("Analyse Suivi-Évaluation", "suivi_evaluation"), ("Analyse d'Opinions", "analyse_opinions")],
                format_func=lambda x: x[0],
                key="long_doc_analysis_type"
            )

            if st.button("Lancer l'Analyse du Long Document", key="long_doc_submit"):
                # Extraire la valeur de la sélection
                selected_analysis_type = analysis_type_dropdown[1]

                model_choice = long_doc_model_selector
                if long_doc_mode == "api":
                    model_choice = MODELS_API[0] if MODELS_API else "api_non_configuree"

                payload = {
                    "analysis_type": selected_analysis_type, 
                    "context": st.session_state.context, 
                    "mode": long_doc_mode, 
                    "model_choice": model_choice
                }
                st.markdown("### Progression de l'Analyse et Résultat Final")
                with st.spinner("Analyse en cours, veuillez patienter..."):
                    with st.container(height=400, border=True):
                        stream_llm_response(f"{BACKEND_URL}/long-document-analysis/", payload)

with viz_tab:
    st.header("Visualisation des Données")
    st.markdown("Générez un nuage de mots sémantique à partir du texte chargé.")

    if not st.session_state.context:
        st.info("Veuillez charger un document pour générer une visualisation.")
    else:
        col1, col2 = st.columns([2, 1])
        with col1:
            synonym_input = st.text_area(
                "Regroupement de synonymes (optionnel)",
                placeholder="Format : mot_cible: synonyme1, synonyme2\nEx: satisfaction: content, heureux",
                height=100
            )
        with col2:
            color_map_input = st.selectbox(
                "Palette de couleurs",
                options=['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Greys', 'Blues', 'Reds', 'YlGn', 'Pastel1'],
                index=0
            )
            if st.button("Générer le Nuage de Mots", type="primary"):
                with st.spinner("Génération du nuage de mots en cours..."):
                    wordcloud_image, status = generate_advanced_wordcloud(
                        st.session_state.context,
                        synonym_input,
                        color_map_input
                    )
                    if wordcloud_image:
                        st.session_state.wordcloud_image = wordcloud_image
                        st.session_state.wordcloud_status = status
                    else:
                        st.session_state.wordcloud_image = None
                        st.warning(status)

        if 'wordcloud_image' in st.session_state and st.session_state.wordcloud_image:
            st.image(st.session_state.wordcloud_image, caption=st.session_state.get('wordcloud_status', 'Nuage de mots'), use_column_width=True)
