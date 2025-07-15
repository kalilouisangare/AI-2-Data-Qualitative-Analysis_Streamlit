# download_model.py

from huggingface_hub import snapshot_download
import os

# Le nom du modèle que nous voulons télécharger
model_id = "fofana/whisper-large-v2-bambara"

print(f"Tentative de téléchargement du modèle : {model_id}")
print("Cela peut prendre beaucoup de temps et d'espace disque...")

try:
    # Cette fonction va télécharger tous les fichiers du modèle et les placer
    # dans le cache de Hugging Face. Elle gère la reprise sur erreur.
    snapshot_download(
        repo_id=model_id,
        repo_type="model",
        local_dir_use_symlinks=False, # Important pour Windows
        resume_download=True, # Tente de reprendre les téléchargements interrompus
        # Si vous avez un token, vous pouvez le spécifier ici, mais le login CLI devrait suffire
        # token="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxx" 
    )
    print("\n\n----------------------------------------------------")
    print("Téléchargement terminé avec succès !")
    print(f"Le modèle '{model_id}' est maintenant dans votre cache local.")
    print("----------------------------------------------------\n")

except Exception as e:
    print("\n\n----------------------------------------------------")
    print(f"ERREUR LORS DU TÉLÉCHARGEMENT : {e}")
    print("Causes possibles :")
    print("1. Le modèle n'existe pas ou est privé (vérifiez le nom).")
    print("2. Problème de réseau persistant (essayez avec un VPN).")
    print("3. Espace disque insuffisant.")
    print("----------------------------------------------------\n")