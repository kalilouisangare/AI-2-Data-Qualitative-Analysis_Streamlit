# run_streamlit.py
import uvicorn
import threading
import time
import os
import subprocess

# On importe l'application FastAPI depuis backend.py
from backend import app as fastapi_app

def run_fastapi():
    """Lance le backend FastAPI avec uvicorn."""
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)

def run_streamlit():
    """Lance l'interface Streamlit en utilisant une commande shell."""
    # Le chemin vers le script principal de Streamlit
    streamlit_script_path = "main_streamlit.py"
    # La commande pour lancer Streamlit
    command = ["streamlit", "run", streamlit_script_path]
    
    print(f"Lancement de la commande : {' '.join(command)}")
    
    # On utilise subprocess.Popen pour lancer Streamlit dans un processus séparé
    process = subprocess.Popen(command)
    # On attend que le processus se termine
    process.wait()

if __name__ == "__main__":
    print("Lancement du backend FastAPI dans un thread...")
    # On lance le backend dans un thread pour qu'il ne bloque pas le reste
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()
    
    # On attend quelques secondes pour être sûr que le backend est prêt
    print("Attente de 3 secondes pour le démarrage du backend...")
    time.sleep(3)
    
    print("Lancement de l'interface Streamlit...")
    # On lance Streamlit dans le thread principal
    run_streamlit()
