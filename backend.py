# backend.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, StreamingResponse
from services.sentiment_analysis_service import sentiment_analysis_service_instance
import pandas as pd
import docx
import io
import os
import tempfile
import fitz
import re

# --- IMPORTS DES SERVICES ---
from services.qa_service import qa_service_instance
from services.transcription_manager import transcription_manager_instance
from services.summarization_service import summarization_service_instance
from services.translation_service import translation_service_instance

# === FONCTION DE PONCTUATION BASIQUE (ajoutée uniquement ici) ===
def _add_basic_punctuation(text: str) -> str:
    """Ajoute une ponctuation minimale pour améliorer la lisibilité."""
    if not text.strip():
        return text
    text = re.sub(r'\s+', ' ', text.strip())
    if not text.endswith(('.', '?', '!', '…')):
        text += '.'
    return text

app = FastAPI(title="API d'Analyse Qualitative")

@app.post("/process-file/")
async def process_file(file: UploadFile = File(...), language: str = Form(...)):
    tmp_path = None
    try:
        content_bytes = await file.read()
        filename = file.filename
        is_audio = file.content_type and file.content_type.startswith('audio/')
        
        if not is_audio:
            print(f"Traitement du document texte : {filename}")
            if filename.endswith('.csv'):
                final_text = pd.read_csv(io.BytesIO(content_bytes)).to_string()
            elif filename.endswith(('.xlsx', '.xls')):
                final_text = pd.read_excel(io.BytesIO(content_bytes)).to_string()
            elif filename.endswith('.docx'):
                doc = docx.Document(io.BytesIO(content_bytes))
                final_text = "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
            elif filename.endswith('.txt'):
                final_text = content_bytes.decode('utf-8', errors='ignore')
            elif filename.lower().endswith('.pdf'):
                doc = fitz.open(stream=content_bytes, filetype="pdf")
                final_text = "".join([page.get_text() for page in doc])
            else:
                return JSONResponse(status_code=400, content={"message": "Format non supporté."})
            if not final_text.strip():
                return JSONResponse(status_code=400, content={"message": "Fichier vide."})
            return {
                "final_text": final_text,
                "transcribed_text": "",
                "translated_text": "",
                "is_audio": False,
                "message": "Document texte traité."
            }

        # --- Audio ---
        print(f"Début du traitement orchestré pour l'audio : {filename}")
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            tmp.write(content_bytes)
            tmp_path = tmp.name

        # Étape 1: Transcription
        print("Orchestration - Étape 1: Transcription")
        transcribed_text = transcription_manager_instance.transcribe(tmp_path, language=language)
        if "Erreur" in transcribed_text or "erreur" in transcribed_text.lower():
            return JSONResponse(status_code=500, content={"message": transcribed_text})

        # === AJOUT DE LA PONCTUATION (uniquement pour le bambara) ===
        if "bambara" in language:
            transcribed_text = _add_basic_punctuation(transcribed_text)

        final_text = transcribed_text
        translated_text = ""

        # Étape 2 & 3: Traduction si bambara
        if "bambara" in language:
            print("Orchestration - Étape 2: Nettoyage avant traduction")
            transcription_manager_instance.clear_cache()
            print("Orchestration - Étape 3: Traduction")
            translated_text = translation_service_instance.translate(
                text=transcribed_text,
                src_lang="bam_Latn",
                target_lang="fra_Latn"
            )
            final_text = translated_text

        return {
            "final_text": final_text,
            "transcribed_text": transcribed_text,
            "translated_text": translated_text,
            "is_audio": True,
            "audio_language": language,
            "message": "Fichier audio traité avec succès."
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": f"Erreur serveur: {e}"})
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

# --- Endpoints d'analyse (inchangés) ---
@app.post("/ask-question/")
async def ask_question(question: str = Form(...), context: str = Form(...), mode: str = Form("local"), model_choice: str = Form("auto")):
    if not context:
        return JSONResponse(status_code=400, content={"message": "Contexte vide."})
    return StreamingResponse(qa_service_instance.ask(context, question, mode, model_choice), media_type="text/event-stream")

@app.post("/summarize-context/")
async def summarize_context(context: str = Form(...), min_length: int = Form(30), max_length: int = Form(150)):
    if not context:
        return JSONResponse(status_code=400, content={"message": "Contexte vide."})
    try:
        summary = summarization_service_instance.summarize(context, min_length, max_length)
        return {"summary": summary}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Erreur: {e}"})

@app.post("/long-document-analysis/")
async def long_document_analysis(analysis_type: str = Form(...), context: str = Form(...), mode: str = Form("local"), model_choice: str = Form("auto")):
    prompts = {
        "resume_general": "Crée une synthèse globale du document suivant.",
        "suivi_evaluation": "Agis en tant qu'expert en Suivi-Évaluation et analyse ce document.",
        "analyse_opinions": "Analyse les opinions exprimées dans ce texte."
    }
    prompt = prompts.get(analysis_type, "Analyse ce document.")
    full_prompt = f"{prompt}\n\nDocument:\n{context}"
    return StreamingResponse(qa_service_instance.ask(full_prompt, "", mode, model_choice), media_type="text/event-stream")

# --- Cache ---
@app.post("/clear-transcription-cache/")
async def clear_transcription_cache():
    transcription_manager_instance.clear_cache()
    return {"message": "Cache transcription nettoyé."}

@app.post("/clear-translation-cache/")
async def clear_translation_cache():
    translation_service_instance.clear_cache()
    return {"message": "Cache traduction nettoyé."}

# --- ANALYSE DE SENTIMENT ---
@app.post("/analyze-sentiment/")
async def analyze_sentiment(context: str = Form(...)):
    """
    Analyse le sentiment d'un texte unique.
    Utilise le modèle bert-base-multilingual-uncased-sentiment.
    Retourne les 5 scores bruts (1 à 5 étoiles).
    """
    if not context:
        return JSONResponse(status_code=400, content={"message": "Contexte vide."})
    try:
        results = sentiment_analysis_service_instance.analyze(context)
        # Normaliser les labels pour l'UI
        normalized = []
        for r in results:
            label = r["label"]
            # Mapping des étoiles vers Positive / Négative / Neutre
            if label in ["1 star", "2 stars"]:
                sentiment = "Négative"
            elif label == "3 stars":
                sentiment = "Neutre"
            else:  # "4 stars", "5 stars"
                sentiment = "Positive"
            normalized.append({
                "label": sentiment,
                "score": round(r["score"] * 100, 2)
            })
        return {"sentiment_scores": normalized}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": f"Erreur: {e}"})
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)