# main_streamlit.py
import streamlit as st
import requests
import os
from dotenv import load_dotenv
from utils_streamlit import generate_advanced_wordcloud
import io

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Outil d'Analyse Qualitative Données",
    page_icon="assets/logo.png",
    layout="wide"
)

# --- CSS AMÉLIORÉ POUR ONGLETS ET VOLE LATÉRAL ---
st.markdown("""
<style>
    /* === CONTENEUR PRINCIPAL DES ONGLETS === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 20px;
        margin-bottom: 25px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 70px;
        padding: 0px 25px;
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        border: 2px solid transparent;
        margin: 0px 2px;
        flex: 1;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255, 255, 255, 0.98);
        transform: translateY(-3px);
        border-color: #667eea;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%) !important;
        color: white !important;
        border-radius: 15px;
        border: 2px solid #ffffff;
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
        transform: scale(1.02);
    }
    
    .stTabs [data-baseweb="tab"] div {
        font-size: 16px;
        font-weight: 700;
        color: #2c3e50;
        text-align: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        letter-spacing: 0.5px;
    }
    
    .stTabs [aria-selected="true"] div {
        color: white !important;
        font-weight: 800;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    /* === VOLE LATÉRAL AMÉLIORÉ === */
    .css-1d391kg, .css-1lcbmhc {
        background: linear-gradient(180deg, #2c3e50 0%, #3498db 100%);
        padding: 20px 15px;
        border-right: 3px solid #2980b9;
    }
    
    /* Titre principal sidebar */
    .sidebar .sidebar-content h1 {
        color: white !important;
        font-size: 24px !important;
        font-weight: 700 !important;
        text-align: center;
        margin-bottom: 30px !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Logo amélioré */
    .sidebar .sidebar-content img {
        border-radius: 20px;
        border: 3px solid #ffffff;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        margin: 0 auto 20px auto !important;
        display: block;
    }
    
    /* File uploader amélioré */
    .stFileUploader {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        padding: 15px !important;
        border: 2px dashed #ecf0f1 !important;
    }
    
    .stFileUploader label {
        color: white !important;
        font-weight: 600 !important;
    }
    
    /* Selectbox amélioré */
    .stSelectbox {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 12px !important;
        padding: 8px !important;
        margin-bottom: 15px !important;
    }
    
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 10px !important;
        border: 2px solid #3498db !important;
    }
    
    /* Boutons améliorés */
    .stButton button {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3) !important;
        width: 100% !important;
        margin: 10px 0 !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(39, 174, 96, 0.5) !important;
        background: linear-gradient(135deg, #229954 0%, #27ae60 100%) !important;
    }
    
    /* Séparateur amélioré */
    .stMarkdown hr {
        border: none !important;
        height: 3px !important;
        background: linear-gradient(90deg, transparent, #ecf0f1, transparent) !important;
        margin: 25px 0 !important;
        border-radius: 10px !important;
    }
    
    /* Section gestion mémoire */
    .sidebar .sidebar-content h2 {
        color: white !important;
        font-size: 20px !important;
        font-weight: 600 !important;
        text-align: center;
        margin: 20px 0 15px 0 !important;
    }
    
    /* Bouton nettoyage mémoire */
    .stButton button[kind="secondary"] {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%) !important;
        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3) !important;
    }
    
    .stButton button[kind="secondary"]:hover {
        box-shadow: 0 8px 25px rgba(231, 76, 60, 0.5) !important;
        background: linear-gradient(135deg, #c0392b 0%, #a93226 100%) !important;
    }
    
    /* Textes et labels */
    .stMarkdown, .stText, .stLabel {
        color: white !important;
    }
    
    /* Conteneurs dans sidebar */
    .css-1r6slb0 {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px !important;
        padding: 15px !important;
        margin: 10px 0 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Animation de fade in */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .sidebar .sidebar-content > * {
        animation: fadeIn 0.6s ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

# --- CHARGEMENT DES VARIABLES D'ENVIRONNEMENT ---
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# --- LISTES DE MODÈLES ---
MODELS_STANDARD = ["auto", "codellama:latest", "llava:latest"]
MODELS_REASONING = ["phi4-mini-reasoning:latest", "deepseek-r1:8b"]
MODELS_API = [os.getenv("GEMINI_MODEL_NAME", "gemini-flash")] if os.getenv("GOOGLE_API_KEY") else ["api_non_configuree"]

# --- INITIALISATION SÛRE DE SESSION STATE ---
if 'final_context' not in st.session_state:
    st.session_state.final_context = ""
if 'transcribed_text' not in st.session_state:
    st.session_state.transcribed_text = ""
if 'translated_text' not in st.session_state:
    st.session_state.translated_text = ""
if 'is_audio' not in st.session_state:
    st.session_state.is_audio = False
if 'audio_language' not in st.session_state:
    st.session_state.audio_language = ""
if 'summary' not in st.session_state:
    st.session_state.summary = ""
if 'wordcloud_image' not in st.session_state:
    st.session_state.wordcloud_image = None
if 'uploaded_audio_bytes' not in st.session_state:
    st.session_state.uploaded_audio_bytes = None

# --- FONCTIONS UTILITAIRES ---
def handle_file_processing(uploaded_file, language_key):
    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    data = {'language': language_key}
    try:
        response = requests.post(f"{BACKEND_URL}/process-file/", files=files, data=data, timeout=3600) # 01h min (3600) au lieu de 10 d'attente (600)
        response.raise_for_status()
        result = response.json()
        
        st.session_state.final_context = result.get("final_text", "")
        st.session_state.transcribed_text = result.get("transcribed_text", "")
        st.session_state.translated_text = result.get("translated_text", "")
        st.session_state.is_audio = result.get("is_audio", False)
        st.session_state.audio_language = result.get("audio_language", "")
        
        st.success(result.get("message", "Fichier traité avec succès !"))
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de communication avec le backend : {e}")

def stream_llm_response(endpoint: str, payload: dict):
    try:
        with requests.post(endpoint, data=payload, stream=True, timeout=900) as response:
            response.raise_for_status()
            st.write_stream(response.iter_content(chunk_size=None, decode_unicode=True))
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de communication avec le LLM : {e}")

# --- INTERFACE UTILISATEUR AMÉLIORÉE ---
with st.sidebar:
    st.image("assets/logo.png", width=140)
    st.title("📤 Chargez un fichier à analyser ici !!!")
    
    # Section upload avec style amélioré
    uploaded_file = st.file_uploader(
        "🗂️ Chargez un document ou un audio", 
        type=['pdf', 'docx', 'txt', 'mp3', 'wav', 'm4a', 'flac', 'ogg'],
        help="Formats supportés : PDF, Word, TXT, MP3, WAV, M4A, FLAC, OGG"
    )
    
    lang_options = {
        "🎯 Audio Français": "french", 
        "🎯 Audio Bambara (Whisper)": "bambara_whisper", 
        "🎯 Audio Bambara (Wav2Vec2)": "bambara_wav2vec2"
    }
    
    selected_lang_key = lang_options[st.selectbox(
        "🌍 Choisir la langue de l'audio", 
        options=list(lang_options.keys()),
        help="Sélectionnez le modèle adapté à la langue de votre audio"
    )]
    
    # Bouton principal amélioré
    if st.button("🚀 Lancer le Traitement", type="primary"):
        if uploaded_file:
            # Réinitialisation propre
            st.session_state.final_context = ""
            st.session_state.transcribed_text = ""
            st.session_state.translated_text = ""
            st.session_state.is_audio = False
            st.session_state.audio_language = ""
            st.session_state.summary = ""
            st.session_state.wordcloud_image = None
            st.session_state.uploaded_audio_bytes = uploaded_file.getvalue() if uploaded_file.type.startswith('audio/') else None
            with st.spinner("🔄 Traitement en cours..."):
                handle_file_processing(uploaded_file, selected_lang_key)
        else:
            st.warning("⚠️ Veuillez charger un fichier avant de continuer.")
    
    st.markdown("---")
    
    # Section gestion mémoire améliorée
    st.header("⚙️ Gestion de la Mémoire")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 Nettoyer Mémoire", help="Libère la mémoire GPU utilisée"):
            try:
                response = requests.post(f"{BACKEND_URL}/clear-transcription-cache/")
                if response.status_code == 200:
                    st.toast("✅ Mémoire nettoyée avec succès !")
                else:
                    st.error("❌ Erreur lors du nettoyage")
            except Exception as e:
                st.error(f"❌ Erreur : {e}")
    
    with col2:
        if st.button("📊 Statut Système", help="Vérifie l'état du système"):
            try:
                response = requests.get(f"{BACKEND_URL}/health/")
                if response.status_code == 200:
                    st.toast("✅ Système opérationnel")
                else:
                    st.warning("⚠️ Système en maintenance")
            except:
                st.error("🔴 Backend non accessible")

# --- ONGLETS PRINCIPAUX AMÉLIORÉS ---
tab_titles = ["🏠 Accueil", "📚 Guide", "📊 Analyses", "📈 Visualisation", "😊 Analyse de Sentiment"]
accueil_tab, guide_tab, analyse_tab, viz_tab, sentiment_tab = st.tabs(tab_titles)

# --- ACCUEIL ---
with accueil_tab:
    st.title("Outil d'Analyse Qualitative Intelligente")
    st.markdown('''
    ## Donnez à vos Données une Voix Intelligente

    Bienvenue sur la plateforme d'analyse de données qualitatives. Cet outil est conçu pour transformer vos documents (textes et audios) et entretiens en informations 
    exploitables, en combinant la puissance des modèles de langage de pointe avec une interface intuitive, le tout en garantissant une confidentialité totale grâce à une exécution 100% locale.
    
    Avec cette pratique vous gagnerez en temps et en precisions par rapport à l'analyse de données classique **(textes longs ou audio de plus de 30 minutes)**. Cet outil vous facilitera la vie car il permet de resume un document de plusieurs centaines de pages,
    d'extraire les informations réelles à travers des audios comme les audios des focus groupes, les entretiens, les feedback des beneficiaires, etc. afin de faciliter la prise de decision dans le contexte des projets/programmes. Et avec des fonctionnalités plus avancées et d'outils supplémentaires comme faire des analyse avec des LLM, des spécialite du texte, etc.


    Cela a été rendu possible par M. Kalilou I Sangare, un professionnel expérimenté avec plus de 8 années au Suivi-Évaluation-Apprentissage-Redevabilité et Data Scientiste afin de ressoudre les problèmes les plus complexes.

    ---

    ### L'Intelligence Artificielle au service de l'Analyse

    Le traitement des données qualitatives – transcriptions d'entretiens, réponses ouvertes, rapports – est traditionnellement un processus long et subjectif. Ce projet propose de le révolutionner en automatisant les tâches ardues. Grâce aux modèles de langage (LLM), nous pouvons comprendre les nuances, identifier les thèmes émergents et synthétiser des concepts complexes.
    ''')

# --- GUIDE ---
with guide_tab:
    st.header("Guide d'Utilisation ")
    st.markdown('''
    ### Comment utiliser cet outil ? 🤔

    #### Étape 1 : Charger le document dont vous souhaiter traité
    - Utilisez la barre latérale pour charger n'importe quel fichier type de fichier autorisé. 
    - Choisir le type de modèle en fonction d'audio que vous avez chargé Audio Français, Audio Bambara (Whisper) ou Audio Bambara (Wav2Vec2). Très important car il va transcrire les audios en texte en fonction de la langue choisie.
    - Cliquez sur **"Lancer le Traitement"**. Le système s'occupe de tout (extraction, transcription, traduction) en une seule étape et affichera les informations dans l'onglet Analyses pour les étapes suivantes

    #### Étape 2 : Analyser le Contenu pour extraires les informations
    Une fois le texte prêt, vous pouvez utiliser les sous-onglets de la section "Analyse" pour :
    - **Résumé** : Créer une synthèse concise.
    - **Interrogation (Q&A)** : Poser des questions directes.
    - **Analyse de Long Document** : Utiliser des prompts complexes.
    - **visualise les informations**: Afficher les images en nuage de mots, classier en fonciton des mots les plus repetitifs et de sentiment positif, negatif ou neutre...
    ''')

# --- ANALYSE ---
with analyse_tab:
    st.header("Analyse du Contenu")
    
    # 🔊 Lecteur audio original
    if st.session_state.uploaded_audio_bytes is not None:
        st.subheader("🎧 Écouter l'audio chargé")
        st.audio(st.session_state.uploaded_audio_bytes, format="audio/wav")
    
    if not st.session_state.final_context:
        st.info("Veuillez charger et traiter un fichier via la barre latérale.")
    else:
        # 🔍 Transcription brute
        if st.session_state.transcribed_text:
            lang_label = "Bambara" if "bambara" in st.session_state.audio_language else "Français"
            st.subheader(f"🔍 Transcription Brute ({lang_label})")
            edited_transcribed = st.text_area(
                f"Texte transcrit en {lang_label}",
                st.session_state.transcribed_text,
                height=150,
                key="transcribed_edit"
            )
            st.download_button(
                label=f"📥 Télécharger la transcription ({lang_label})",
                data=edited_transcribed,
                file_name=f"transcription_{lang_label.lower()}.txt",
                mime="text/plain"
            )

        # 🔄 Traduction (bambara → français)
        if st.session_state.translated_text:
            st.subheader("🔄 Traduction (Bambara → Français)")
            edited_translated = st.text_area(
                "Texte traduit en français",
                st.session_state.translated_text,
                height=150,
                key="translated_edit"
            )
            st.download_button(
                label="📥 Télécharger la traduction (français)",
                data=edited_translated,
                file_name="traduction_francais.txt",
                mime="text/plain"
            )

        # 📄 Texte final pour analyse
        st.markdown("---")
        st.subheader("📄 Texte Final pour l'Analyse")
        st.text_area(
            "Ce texte est utilisé pour toutes les analyses",
            st.session_state.final_context,
            height=150,
            disabled=True,
            key="final_context_area"
        )
        st.download_button(
            label="📥 Télécharger le texte final (.txt)",
            data=st.session_state.final_context,
            file_name="texte_final.txt",
            mime="text/plain"
        )

        # Onglets d'analyse avec style amélioré
        st.markdown("""
        <style>
        /* Style pour les sous-onglets d'analyse */
        .stTabs [data-baseweb="tab-list"] {
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%) !important;
            border-radius: 12px;
            padding: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        analysis_tabs = st.tabs(["📝 Résumé", "❓ Interrogation (Q&A)", "📋 Analyse de Long Document"])
        
        with analysis_tabs[0]:
            st.subheader("Résumé Automatique")
            min_len = st.slider("Longueur minimale", 5, 100, 20, key="min_len_sum")
            max_len = st.slider("Longueur maximale", 50, 150, 120, key="max_len_sum")
            if st.button("Générer le résumé", key="summarize_button"):
                payload = {"context": st.session_state.final_context, "min_length": min_len, "max_length": max_len}
                try:
                    with st.spinner("Génération du résumé..."):
                        response = requests.post(f"{BACKEND_URL}/summarize-context/", data=payload)
                        response.raise_for_status()
                        result = response.json()
                        st.session_state.summary = result.get("summary", "")
                        st.success("Résumé généré !")
                except requests.exceptions.RequestException as e:
                    st.error(f"Erreur : {e}")
            if st.session_state.summary:
                st.text_area("Résultat du Résumé", st.session_state.summary, height=200, key="summary_area")
                st.download_button(
                    label="📥 Télécharger le résumé (.txt)",
                    data=st.session_state.summary,
                    file_name="resume.txt",
                    mime="text/plain"
                )

        with analysis_tabs[1]:
            st.subheader("Interrogation (Q&A)")
            qa_mode = st.radio("Mode", ["local", "api"], key="qa_mode", horizontal=True)
            model_selector = st.selectbox("Modèle", MODELS_STANDARD if qa_mode == "local" else MODELS_API, key="qa_model")
            question = st.text_area("Votre question", height=100, key="qa_question")
            if st.button("Obtenir une Réponse", key="qa_submit") and question.strip():
                payload = {"question": question, "context": st.session_state.final_context, "mode": qa_mode, "model_choice": model_selector}
                st.markdown("### Réponse")
                with st.container(height=300, border=True):
                    stream_llm_response(f"{BACKEND_URL}/ask-question/", payload)

        with analysis_tabs[2]:
            st.subheader("Analyse de Long Document")
            long_mode = st.radio("Mode", ["local", "api"], key="long_mode", horizontal=True)
            long_model = st.selectbox("Modèle", MODELS_REASONING if long_mode == "local" else MODELS_API, key="long_model")
            analysis_type = st.selectbox(
                "Type d'analyse",
                [("Synthèse Générale", "resume_general"), ("Suivi-Évaluation", "suivi_evaluation"), ("Analyse d'Opinions", "analyse_opinions")],
                format_func=lambda x: x[0],
                key="analysis_type"
            )
            if st.button("Lancer l'Analyse", key="long_submit"):
                payload = {"analysis_type": analysis_type[1], "context": st.session_state.final_context, "mode": long_mode, "model_choice": long_model}
                st.markdown("### Résultat")
                with st.container(height=300, border=True):
                    stream_llm_response(f"{BACKEND_URL}/long-document-analysis/", payload)

# --- VISUALISATION ---
with viz_tab:
    st.header("Visualisation des Données")
    if not st.session_state.final_context:
        st.info("Un texte est nécessaire pour la visualisation.")
    else:
        synonym_str = st.text_area("Gestion des Synonymes (optionnel)", height=100, key="synonym_input")
        colormap = st.selectbox("Palette de Couleurs", ["viridis", "plasma", "inferno", "magma", "Blues", "Greens", "Reds"], key="colormap")
        if st.button("Générer le Nuage de Mots", key="generate_wordcloud"):
            with st.spinner("Génération..."):
                image, msg = generate_advanced_wordcloud(st.session_state.final_context, synonym_str, colormap)
                if image:
                    st.session_state.wordcloud_image = image
                    st.image(image, caption=msg, use_column_width=True)
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button(
                        label="📥 Télécharger le nuage de mots (.png)",
                        data=buf.getvalue(),
                        file_name="nuage_mots.png",
                        mime="image/png"
                    )
                else:
                    st.warning(msg)

# --- ANALYSE DE SENTIMENT ---
with sentiment_tab:
    st.header("📊 Analyse de Sentiment")
    if not st.session_state.final_context:
        st.info("Veuillez charger un fichier pour activer l'analyse de sentiment.")
    else:
        st.text_area("Texte analysé", st.session_state.final_context, height=150, disabled=True)
        
        if st.button("🔍 Lancer l'analyse de sentiment", type="primary"):
            with st.spinner("Analyse en cours..."):
                try:
                    # --- ÉTAPE 1 : Découpage en phrases ---
                    raw_text = st.session_state.final_context.strip()
                    sentences = [s.strip() for s in raw_text.replace('\n', '. ').split('.') if s.strip()]
                    if not sentences:
                        st.warning("Aucune phrase détectée.")
                        st.stop()

                    # --- ÉTAPE 2 : Analyse de sentiment par phrase ---
                    sentiment_results = []
                    for sent in sentences:
                        response = requests.post(
                            f"{BACKEND_URL}/analyze-sentiment/",
                            data={"context": sent}
                        )
                        if response.status_code == 200:
                            res = response.json()
                            scores = res.get("sentiment_scores", [])
                            if scores:
                                # Trouver la classe avec le score max
                                best = max(scores, key=lambda x: x["score"])
                                sentiment_results.append({
                                    "sentence": sent,
                                    "sentiment": best["label"],
                                    "confidence": best["score"]
                                })
                        else:
                            sentiment_results.append({
                                "sentence": sent,
                                "sentiment": "Erreur",
                                "confidence": 0.0
                            })

                    # --- ÉTAPE 3 : Comptage des sentiments ---
                    from collections import Counter
                    sentiment_counts = Counter([r["sentiment"] for r in sentiment_results])
                    total_phrases = len(sentiment_results)

                    # --- ÉTAPE 4 : Extraction des mots fréquents ---
                    try:
                        from utils_streamlit import load_spacy_model
                        nlp = load_spacy_model()
                        all_words = []
                        for sent in sentences:
                            doc = nlp(sent.lower())
                            tokens = [
                                token.lemma_.lower()
                                for token in doc
                                if token.is_alpha and not token.is_stop and len(token.text) > 2
                            ]
                            all_words.extend(tokens)
                        word_freq = Counter(all_words).most_common(20)
                    except Exception as e:
                        st.warning(f"Erreur dans l'extraction des mots : {e}")
                        word_freq = []

                    # --- AFFICHAGE ---
                    st.subheader("📈 Résultats de l'analyse")

                    # Comptage
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total de phrases", total_phrases)
                        for label in ["Positive", "Négative", "Neutre", "Erreur"]:
                            count = sentiment_counts.get(label, 0)
                            if count > 0:
                                st.metric(f"Phrases {label}", count)

                    # Mots fréquents
                    with col2:
                        if word_freq:
                            st.write("**Mots les plus fréquents :**")
                            for word, freq in word_freq[:10]:
                                st.write(f"- `{word}` : {freq} fois")

                    # Tableau détaillé (optionnel)
                    with st.expander("Voir les phrases et leurs sentiments"):
                        for r in sentiment_results:
                            st.markdown(f"**{r['sentiment']}** ({r['confidence']:.1%}) : {r['sentence']}")

                    # Téléchargement CSV
                    import pandas as pd
                    df_results = pd.DataFrame(sentiment_results)
                    csv = df_results.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Télécharger l'analyse détaillée (.csv)",
                        data=csv,
                        file_name="analyse_sentiment_phrases.csv",
                        mime="text/csv"
                    )

                    # WordCloud (optionnel)
                    if word_freq:
                        try:
                            from wordcloud import WordCloud
                            import matplotlib.pyplot as plt
                            freq_dict = dict(word_freq)
                            wc = WordCloud(width=600, height=300, background_color='white', colormap='viridis').generate_from_frequencies(freq_dict)
                            fig, ax = plt.subplots(figsize=(10, 5))
                            ax.imshow(wc, interpolation='bilinear')
                            ax.axis("off")
                            st.pyplot(fig)
                            plt.close(fig)
                        except Exception as e:
                            st.warning(f"Impossible de générer le nuage de mots : {e}")

                except Exception as e:
                    st.error(f"Erreur lors de l'analyse : {e}")