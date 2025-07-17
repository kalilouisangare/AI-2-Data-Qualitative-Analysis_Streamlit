from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, StreamingResponse
import pandas as pd
import docx
import io
import os
import tempfile
import fitz

from services.qa_service import qa_service_instance
from services.transcription_service import transcription_service_instance
from services.summarization_service import summarization_service_instance

app = FastAPI(title="API d'Analyse Qualitative")

# --- LES PROMPTS SONT BIEN STOCKÉS ICI ---
ANALYSIS_PROMPTS = {
    "resume_general": """Ta mission est de créer une synthèse globale et structurée à partir des résumés partiels d'un long document. Commence par une introduction présentant le sujet principal, puis développe les 3 à 5 thèmes les plus importants en te basant sur le contenu fourni, et termine par une conclusion générale.

Voici les résumés partiels à utiliser comme source unique :
{summaries}

Rédige maintenant la **synthèse globale et structurée**.""",

    "suivi_evaluation": """Agis en tant qu'expert en Suivi-Évaluation. En te basant sur les résumés du rapport ci-dessous, identifie les principales recommandations formulées, les risques mentionnés, et les leçons apprises. Structure ta réponse en trois sections claires avec des titres : Recommandations, Risques, et Leçons Apprises.

Voici les résumés partiels à utiliser comme source unique :
{summaries}

Rédige maintenant ton **analyse de Suivi-Évaluation**.""",

    "analyse_opinions": """Tu es un sociologue spécialisé dans l'analyse de discours. Analyse les résumés d'entretiens fournis ci-dessous. Identifie et regroupe les opinions positives et les opinions négatives exprimées par les participants concernant le projet. Présente le résultat sous forme de deux listes à puces distinctes, avec les titres "Points Positifs" et "Points Négatifs".

Voici les résumés partiels des entretiens :
{summaries}

Rédige maintenant ton **analyse d'opinions**."""
}

def chunk_text(text: str, chunk_size: int = 3000, chunk_overlap: int = 300):
    if not isinstance(text, str): return []
    if len(text) <= chunk_size: return [text]
    chunks = []; start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    return chunks

@app.post("/upload-file/")
async def upload_and_process_file(file: UploadFile = File(...), language: str = Form("auto")):
    try:
        content_bytes = await file.read()
        filename = file.filename; is_audio_context = False; tmp_path = None

        if filename.endswith('.csv'): current_context = pd.read_csv(io.BytesIO(content_bytes)).to_string()
        elif filename.endswith(('.xlsx', '.xls')): current_context = pd.read_excel(io.BytesIO(content_bytes)).to_string()
        elif filename.endswith('.docx'):
            doc = docx.Document(io.BytesIO(content_bytes))
            current_context = "\n\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
        elif filename.endswith('.txt'): current_context = content_bytes.decode('utf-8', errors='ignore')
        elif filename.lower().endswith('.pdf'):
            doc = fitz.open(stream=content_bytes, filetype="pdf")
            current_context = "".join([page.get_text() for page in doc])
        elif filename.lower().endswith(('.mp3', '.wav', '.m4a', '.flac', '.ogg')):
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                tmp.write(content_bytes); tmp_path = tmp.name
            current_context = transcription_service_instance.transcribe(tmp_path, language=language)
            is_audio_context = True
        else:
            return JSONResponse(status_code=400, content={"message": "Format de fichier non supporté."})

        if not current_context.strip():
            return JSONResponse(status_code=400, content={"message": "Fichier vide ou contenu non extrait."})

        return {"message": "Fichier traité.", "full_text": current_context, "is_audio": is_audio_context}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Erreur: {e}"})
    finally:
        if tmp_path and os.path.exists(tmp_path): os.remove(tmp_path)

async def long_document_streamer(analysis_type, context, mode, model_choice):
    if not context:
        yield "ERREUR : Le contexte est vide."
        return

    if mode == "api":
        yield "Mode API sélectionné. Envoi du document complet...\n\n"
        prompt_template = ANALYSIS_PROMPTS.get(analysis_type, ANALYSIS_PROMPTS["resume_general"])
        final_prompt = prompt_template.format(summaries=context)
        # ✅ Correction : On utilise `for` au lieu de `async for`
        for token in qa_service_instance.ask(final_prompt, "", mode, model_choice):
            yield token
    else:
        yield "Mode Local sélectionné. Lancement du processus Map-Reduce...\n"
        yield "Étape 1/3 : Découpage du document...\n"
        text_chunks = chunk_text(context)
        yield f"Document découpé en {len(text_chunks)} morceaux.\n\n"

        progress_display = f"Document découpé en {len(text_chunks)} morceaux.\n\nÉtape 2/3 : Création des résumés partiels...\n"
        yield progress_display

        intermediate_summaries = []
        for i, chunk in enumerate(text_chunks):
            status_message = f"  - Traitement du morceau {i+1}/{len(text_chunks)}...\n"
            progress_display += status_message; yield progress_display
            try:
                summary_chunk = summarization_service_instance.summarize(chunk, min_length=40, max_length=200)
                intermediate_summaries.append(summary_chunk)
                result_message = f"    -> Terminé.\n"
            except Exception as e:
                result_message = f"    -> Erreur sur le morceau {i+1}.\n"; intermediate_summaries.append(f"Erreur d'analyse: {e}")
            progress_display += result_message; yield progress_display

        final_synthesis_header = "\n\n----------------------------------\nÉtape 3/3 : Synthèse finale...\n----------------------------------\n\n"
        progress_display += final_synthesis_header; yield progress_display

        combined_summaries = "\n\n---\n\n".join(intermediate_summaries)
        final_prompt_template = ANALYSIS_PROMPTS.get(analysis_type, ANALYSIS_PROMPTS["resume_general"])
        final_prompt = final_prompt_template.format(summaries=combined_summaries)

        # ✅ Correction : On utilise `for` au lieu de `async for`
        for token in qa_service_instance.ask(final_prompt, "", mode, model_choice):
            progress_display += token
            yield progress_display

@app.post("/long-document-analysis/")
async def long_document_analysis(analysis_type: str = Form(...), context: str = Form(...), mode: str = Form("local"), model_choice: str = Form("auto")):
    return StreamingResponse(long_document_streamer(analysis_type, context, mode, model_choice), media_type="text/event-stream")

@app.post("/ask-question/")
async def ask_question(question: str = Form(...), context: str = Form(...), mode: str = Form("local"), model_choice: str = Form("auto")):
    if not context:
        return JSONResponse(status_code=400, content={"message": "Le contexte est vide."})
    return StreamingResponse(qa_service_instance.ask(context, question, mode, model_choice), media_type="text/event-stream")

@app.post("/summarize-context/")
async def summarize_context(context: str = Form(...), is_audio: bool = Form(...), min_length: int = Form(30), max_length: int = Form(150)):
    if not is_audio:
        return JSONResponse(status_code=400, content={"message": "Le résumé automatique est uniquement disponible pour les fichiers audio transcrits."})
    if not context:
        return JSONResponse(status_code=400, content={"message": "Le contexte est vide."})
    try:
        summary = summarization_service_instance.summarize(context, min_length, max_length)
        return {"summary": summary}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Erreur: {e}"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
