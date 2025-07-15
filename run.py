# run.py
import uvicorn
import threading
import time

# On importe l'application FastAPI depuis backend.py et l'interface Gradio depuis main.py
from backend import app as fastapi_app
from main import demo as gradio_interface

def run_gradio():
    """Lance l'interface Gradio."""
    # On utilise share=False pour ne pas créer de lien public
    gradio_interface.launch(share=False)

def run_fastapi():
    """Lance le backend FastAPI."""
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    print("Lancement du backend FastAPI dans un thread...")
    # On lance le backend dans un thread pour qu'il ne bloque pas le reste
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()
    
    # On attend une seconde pour être sûr que le backend est prêt
    time.sleep(2) 
    
    print("Lancement de l'interface Gradio...")
    # On lance Gradio dans le thread principal
    run_gradio()