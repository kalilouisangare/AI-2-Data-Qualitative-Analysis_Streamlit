# main.py
import gradio as gr
import requests
import os
import pandas as pd
from docx import Document
from wordcloud import WordCloud
from PIL import Image
import spacy
from dotenv import load_dotenv
from utils import generate_advanced_wordcloud, save_text_to_file

# --- CONFIGURATION AU DÉMARRAGE ---
load_dotenv()
MODELS_STANDARD = ["auto", "codellama:latest", "llava:latest"]
MODELS_REASONING = ["phi4-mini-reasoning:latest", "deepseek-r1:8b"]
MODELS_API = []
if os.getenv("GOOGLE_API_KEY"): MODELS_API.append("gemini-flash")
if not MODELS_API: MODELS_API = ["api_non_configuree"]

BACKEND_URL = "http://127.0.0.1:8000"

# --- Fonctions de communication ---
def upload_file_to_backend(file, language):
    if file is None: return "Veuillez sélectionner un fichier.", "", False, "", gr.update(selected=2)
    try:
        files_payload = {'file': (os.path.basename(file.name), open(file.name, 'rb'))}
        data_payload = {'language': language}
        response = requests.post(f"{BACKEND_URL}/upload-file/", files=files_payload, data=data_payload)
        response.raise_for_status()
        result = response.json()
        is_audio = result.get("is_audio", False)
        full_text = result.get("full_text", "")
        return result.get("message", "Erreur"), full_text[:1000], is_audio, full_text
    except Exception as e:
        gr.Error(f"Erreur de communication : {e}")
        return "Erreur", "", False, ""

def stream_llm_response(endpoint: str, payload: dict):
    full_text = ""
    try:
        with requests.post(endpoint, data=payload, stream=True, timeout=900) as response:
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                if chunk:
                    full_text += chunk
                    yield full_text
    except Exception as e:
        gr.Error(f"Erreur de communication avec le LLM : {e}")
        yield f"Erreur : {e}"

def ask_question_to_backend_stream(question, context, mode, model_choice):
    if not question: gr.Warning("Veuillez poser une question."); yield ""; return
    if not context: gr.Warning("Veuillez d'abord charger un document."); yield ""; return
    if mode == "api": model_choice = MODELS_API[0] if MODELS_API else "api_non_configuree"
    payload = {"question": question, "context": context, "mode": mode, "model_choice": model_choice}
    yield from stream_llm_response(f"{BACKEND_URL}/ask-question/", payload)

def long_document_analysis_stream(analysis_type, context, mode, model_choice):
    if not analysis_type: gr.Warning("Veuillez choisir un type d'analyse."); yield ""; return
    if not context: gr.Warning("Veuillez d'abord charger un document."); yield ""; return
    if mode == "api": model_choice = MODELS_API[0] if MODELS_API else "api_non_configuree"
    payload = {"analysis_type": analysis_type, "context": context, "mode": mode, "model_choice": model_choice}
    yield from stream_llm_response(f"{BACKEND_URL}/long-document-analysis/", payload)
    
def summarize_context_from_backend(context, is_audio, min_len, max_len):
    if not context: gr.Warning("Veuillez d'abord charger un document."); return ""
    if not is_audio: gr.Warning("Le résumé auto n'est activé que pour les fichiers audio."); return ""
    payload = {"context": context, "is_audio": is_audio, "min_length": min_len, "max_length": max_len}
    try:
        r = requests.post(f"{BACKEND_URL}/summarize-context/", data=payload).json()
        if "detail" in r or ("message" in r and r.get("status_code", 200) != 200):
            gr.Warning(r.get("detail") or r.get("message")); return ""
        return r.get("summary", "Pas de résumé.")
    except Exception as e:
        gr.Error(f"Erreur de communication : {e}"); return ""
    
def update_model_choices(mode, model_list_name):
    if model_list_name == "reasoning": local_list = MODELS_REASONING
    else: local_list = MODELS_STANDARD
    if mode == "local": return gr.update(choices=local_list, value=local_list[0])
    else: return gr.update(choices=MODELS_API, value=MODELS_API[0])

# --- Interface Gradio ---
with gr.Blocks(theme=gr.themes.Soft(), title="Analyse Qualitative") as demo:
    context_state = gr.State("")
    is_audio_state = gr.State(False)
    
    with gr.Row(equal_height=False):
        gr.HTML("""<div style="display: flex; align-items: center; padding: 10px;"><img src="file/assets/logo.png" alt="Logo" style="height: 70px; margin-right: 20px;"/><div><h1 style="margin: 0; font-size: 2em;">Outil d'Analyse Qualitative Intelligente</h1></div></div>""")

    with gr.Tabs() as main_tabs:
        with gr.TabItem("📖 Accueil & Présentation", id=0):
            with gr.Row():
                with gr.Column():
                    gr.Markdown(
                        """
                        ## Donnez à vos Données une Voix Intelligente
                        Bienvenue sur la plateforme d'analyse de données qualitatives. Cet outil est conçu pour transformer vos documents et entretiens en informations exploitables, en combinant la puissance des modèles de langage de pointe avec une interface intuitive, le tout en garantissant une confidentialité totale grâce à une exécution 100% locale.
                        
                        *Créé par Kalilou I Sangare, un professionnel du Suivi-Evaluation et Data Scientiste avec l'appui technique de l'IA Générative de Google Gemini 2.5 Pro.*
                        ---
                        ### L'Intelligence Artificielle au service de l'Analyse
                        Le traitement des données qualitatives – transcriptions d'entretiens, réponses ouvertes, rapports – est traditionnellement un processus long et subjectif. Ce projet propose de le révolutionner en automatisant les tâches ardues. Grâce aux modèles de langage (LLM), nous pouvons comprendre les nuances, identifier les thèmes émergents et synthétiser des concepts complexes.
                        
                        ### De la Donnée Brute à la Décision
                        Notre outil facilite la transition de la donnée brute à la décision éclairée. Un rapport de 100 pages peut être résumé en quelques minutes via la fonction d'analyse de longs documents. Les réponses de centaines de personnes à une enquête peuvent être analysées pour en faire ressortir les tendances principales.
                        
                        ### Une Boîte à Outils Complète et Locale
                        La plateforme orchestre différents modèles d'IA spécialisés. Un modèle de transcription convertit la parole en texte. Un modèle de résumé synthétise les points clés. Enfin, des LLM généralistes ou de raisonnement permettent une interrogation flexible des données, le tout sur votre machine, assurant que vos données sensibles restent confidentielles.
                        
                        ### Flexibilité et Puissance
                        Que vous ayez besoin d'une réponse rapide à une question simple, d'un résumé automatique, ou d'une analyse en profondeur avec un raisonnement détaillé, l'outil s'adapte à vos besoins.
                        
                        ### Comment Commencer ?
                        Naviguez simplement à travers les onglets ci-dessus. Commencez par **"Étape 1 : Charger vos Données"** pour importer vos fichiers et laissez-vous guider.
                        """
                    )

        with gr.TabItem("💡 Aide / Guide", id=1):
            gr.Markdown(
                """
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
                """
            )

        with gr.TabItem("Étape 1 : Charger vos Données", id=2):
            with gr.Row():
                with gr.Column(scale=1):
                    file_input = gr.File(label="Uploader un fichier (pdf, txt, docx, etc.)")
                    lang_selector = gr.Dropdown(label="Langue de l'audio", choices=[("Auto", "auto"), ("Français", "fr"), ("Anglais", "en")], value="auto")
                    upload_button = gr.Button("Charger et Traiter", variant="primary")
                    upload_status = gr.Textbox(label="Statut", interactive=False)
                with gr.Column(scale=2):
                    gr.Markdown("### Contexte / Transcription")
                    file_preview = gr.Textbox(label=None, lines=15, interactive=False, placeholder="L'aperçu du document chargé apparaîtra ici...")
                    with gr.Row():
                        export_format_preview = gr.Radio([".txt", ".docx", ".csv"], label="Format", value=".txt"); export_button_preview = gr.Button("Exporter")
                    download_link_preview = gr.File(label="Télécharger", interactive=False)

        with gr.TabItem("Étape 2 : Analyser le Contenu", id=3):
            with gr.Tabs():
                with gr.TabItem("2.1 Résumé Automatique (Audio)", visible=False) as resume_tab:
                    gr.Markdown("Générez un résumé rapide du fichier audio transcrit.")
                    with gr.Row():
                        min_len_slider = gr.Slider(5, 100, value=20, step=5, label="Longueur Min"); max_len_slider = gr.Slider(50, 512, value=120, step=10, label="Longueur Max")
                    summarize_button = gr.Button("Générer le Résumé", variant="primary")
                    gr.Markdown("### Résultat du Résumé")
                    summary_output = gr.Textbox(label=None, lines=15, interactive=False)
                    with gr.Row():
                        export_format_summary = gr.Radio([".txt", ".docx", ".csv"], label="Format", value=".txt"); export_button_summary = gr.Button("Exporter")
                    download_link_summary = gr.File(label="Télécharger", interactive=False)
                
                with gr.TabItem("2.2 Interrogation Standard (Q&A)"):
                    gr.Markdown("Posez des questions directes aux LLM standards.")
                    with gr.Row():
                        qa_mode = gr.Radio(["local", "api"], label="Mode", value="local")
                        model_selector = gr.Dropdown(MODELS_STANDARD, label="Modèle Standard", value=MODELS_STANDARD[0])
                    question_box = gr.Textbox(label="Question", lines=2, placeholder="Ex: Quels sont les points clés ?")
                    with gr.Row():
                        ask_button = gr.Button("Obtenir une Réponse", variant="primary"); stop_ask = gr.Button("Stop", variant="stop")
                    gr.Markdown("### Réponse du Modèle")
                    answer_box = gr.Textbox(label=None, lines=15, interactive=False)
                    with gr.Row():
                        export_format_qa = gr.Radio([".txt", ".docx", ".csv"], label="Format", value=".txt"); export_button_qa = gr.Button("Exporter")
                    download_link_qa = gr.File(label="Télécharger", interactive=False)

                with gr.TabItem("2.3 Analyse par Raisonnement"):
                    gr.Markdown("Posez des questions complexes aux modèles spécialisés.")
                    with gr.Row():
                        reasoning_mode = gr.Radio(["local"], label="Mode", value="local", interactive=False)
                        reasoning_model_selector = gr.Dropdown(MODELS_REASONING, label="Modèle de Raisonnement", value=MODELS_REASONING[0])
                    reasoning_question_box = gr.Textbox(label="Demande / Instruction", lines=3, placeholder="Ex: Analyse les thèmes principaux et explique ton raisonnement.")
                    with gr.Row():
                        reasoning_button = gr.Button("Lancer l'Analyse", variant="primary"); stop_reasoning = gr.Button("Stop", variant="stop")
                    gr.Markdown("### Sortie Complète du Modèle")
                    reasoning_answer_box = gr.Textbox(label=None, lines=20, interactive=False)
                    with gr.Row():
                        export_format_reasoning = gr.Radio([".txt", ".docx", ".csv"], label="Format", value=".txt"); export_button_reasoning = gr.Button("Exporter")
                    download_link_reasoning = gr.File(label="Télécharger", interactive=False)
                
                with gr.TabItem("2.4 Analyse de Long Document"):
                    gr.Markdown("Analysez des documents volumineux. Le mode API est recommandé pour sa rapidité.")
                    with gr.Row():
                        long_doc_mode = gr.Radio(["local", "api"], label="Mode", value="local")
                        long_doc_model_selector = gr.Dropdown(MODELS_STANDARD, label="Modèle", value="codellama:latest")
                    analysis_type_dropdown = gr.Dropdown(
                        choices=[("Synthèse Générale", "resume_general"), ("Analyse Suivi-Évaluation", "suivi_evaluation"), ("Analyse d'Opinions", "analyse_opinions")],
                        label="Type d'Analyse Prédéfinie",
                        value="resume_general"
                    )
                    with gr.Row():
                        long_doc_button = gr.Button("Lancer l'Analyse du Long Document", variant="primary"); stop_long_doc = gr.Button("Stop", variant="stop")
                    gr.Markdown("### Progression de l'Analyse et Résultat Final")
                    long_doc_answer_box = gr.Textbox(label=None, lines=20, interactive=False)
                    with gr.Row():
                        export_format_long_doc = gr.Radio([".txt", ".docx", ".csv"], label="Format", value=".txt"); export_button_long_doc = gr.Button("Exporter")
                    download_link_long_doc = gr.File(label="Télécharger", interactive=False)

        with gr.TabItem("Étape 3 : Visualiser les Données", id=4):
            gr.Markdown("Générez un nuage de mots sémantique à partir du texte chargé.")
            with gr.Row():
                with gr.Column(scale=2):
                    synonym_input = gr.Textbox(label="Regroupement de synonymes (optionnel)", placeholder="Format : mot_cible: synonyme1, synonyme2\nEx: satisfaction: content, heureux", lines=4)
                with gr.Column(scale=1):
                    color_map_input = gr.Dropdown(label="Palette de couleurs", choices=['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Greys', 'Blues', 'Reds', 'YlGn', 'Pastel1'], value='viridis')
                    wordcloud_button = gr.Button("Générer le Nuage de Mots", variant="primary")
            wordcloud_status = gr.Textbox(label="Statut", interactive=False)
            wordcloud_output = gr.Image(label="Nuage de Mots Généré", type="pil")

    # --- Logique des Interactions ---
    qa_mode.change(fn=lambda mode: update_model_choices(mode, "standard"), inputs=qa_mode, outputs=model_selector, show_progress="minimal")
    long_doc_mode.change(fn=lambda mode: update_model_choices(mode, "long_doc"), inputs=long_doc_mode, outputs=long_doc_model_selector, show_progress="minimal")
    
    upload_button.click(fn=upload_file_to_backend, inputs=[file_input, lang_selector], outputs=[upload_status, file_preview, is_audio_state, context_state], show_progress="minimal").then(lambda: gr.update(selected=3), outputs=[main_tabs])
    
    summarize_button.click(fn=summarize_context_from_backend, inputs=[context_state, is_audio_state, min_len_slider, max_len_slider], outputs=[summary_output], show_progress="minimal")
    
    ask_event = ask_button.click(fn=ask_question_to_backend_stream, inputs=[question_box, context_state, qa_mode, model_selector], outputs=[answer_box])
    stop_ask.click(fn=None, inputs=None, outputs=None, cancels=[ask_event])

    reasoning_event = reasoning_button.click(fn=ask_question_to_backend_stream, inputs=[reasoning_question_box, context_state, reasoning_mode, reasoning_model_selector], outputs=[reasoning_answer_box])
    stop_reasoning.click(fn=None, inputs=None, outputs=None, cancels=[reasoning_event])
    
    long_doc_event = long_doc_button.click(fn=long_document_analysis_stream, inputs=[analysis_type_dropdown, context_state, long_doc_mode, long_doc_model_selector], outputs=[long_doc_answer_box])
    stop_long_doc.click(fn=None, inputs=None, outputs=None, cancels=[long_doc_event])
    
    wordcloud_event = wordcloud_button.click(fn=generate_advanced_wordcloud, inputs=[context_state, synonym_input, color_map_input], outputs=[wordcloud_output, wordcloud_status], show_progress="minimal")
    
    export_button_preview.click(fn=save_text_to_file, inputs=[file_preview, export_format_preview], outputs=[download_link_preview])
    export_button_summary.click(fn=save_text_to_file, inputs=[summary_output, export_format_summary], outputs=[download_link_summary])
    export_button_qa.click(fn=save_text_to_file, inputs=[answer_box, export_format_qa], outputs=[download_link_qa])
    export_button_reasoning.click(fn=save_text_to_file, inputs=[reasoning_answer_box, export_format_reasoning], outputs=[download_link_reasoning])
    export_button_long_doc.click(fn=save_text_to_file, inputs=[long_doc_answer_box, export_format_long_doc], outputs=[download_link_long_doc])

if __name__ == "__main__":
    demo.launch(debug=True)