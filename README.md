# Projet d'Analyse Qualitative Automatisée

Cet outil permet de réaliser une analyse qualitative complète sur des documents texte ou des fichiers audio. Il automatise les tâches de transcription, traduction, résumé, et permet de poser des questions directement sur le contenu de vos documents.

## ✨ Fonctionnalités

*   **Transcription Audio** : Convertit les fichiers audio en texte.
*   **Traduction** : Traduit le contenu textuel dans la langue de votre choix.
*   **Résumé Automatique** : Génère des résumés concis de longs documents.
*   **Questions & Réponses (QA)** : Obtenez des réponses précises à vos questions basées sur les documents fournis.
*   **Synthèse Vocale (TTS)** : Convertit le texte des résultats en fichier audio.

## 🚀 Installation

Suivez ces étapes pour configurer l'environnement et lancer le projet.

### 1. Prérequis

*   [Python 3.8+](https://www.python.org/)
*   [Git](https://git-scm.com/)

### 2. Cloner le Dépôt

```bash
git clone https://github.com/kalilouisangare/AI-2-Data-Qualitative-Analysis_Streamlit
cd AI-2-Data-Qualitative-Analysis_Streamlit
```

### 3. Créer et Activer l'Environnement Virtuel

*   **Windows** :
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
*   **macOS / Linux** :
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

### 4. Installer les Dépendances

Assurez-vous que votre environnement virtuel est activé avant de lancer cette commande.
```bash
pip install -r requirements.txt
```

### 5. Télécharger le Modèle

Un modèle de langue est nécessaire pour l'analyse. Exécutez le script suivant pour le télécharger :
```bash
python download_model.py
```

## 📖 Mode d'emploi

Cet outil peut être lancé de deux manières : via une interface web conviviale ou en ligne de commande.

### Interface Web (Recommandé)

1.  **Lancer le serveur** : Exécutez le script `backend.py` pour démarrer le serveur web local.
    ```bash
    python backend.py
    ```
2.  **Accéder à l'application** : Ouvrez votre navigateur et rendez-vous à l'adresse suivante pour utiliser l'interface interactive.
    [http://127.0.0.1:7860/](http://127.0.0.1:7860/)

### Ligne de Commande

1.  **Ajouter vos données** : Placez tous vos fichiers (par exemple `.wav`, `.mp3`, `.txt`, `.docx`) dans le dossier `data/`.
2.  **Lancer l'analyse** : Exécutez le script `main.py` pour démarrer le traitement.
    ```bash
    python main.py
    ```
3.  **Consulter les résultats** : Une fois l'analyse terminée, les résultats seront compilés dans le fichier `export.docx`.

## 🔧 Configuration des Modèles

Cet outil peut être configuré pour utiliser des modèles de langage locaux via **Ollama** ou des API externes comme **Gemini** et **OpenAI**.

### Utilisation avec Ollama (Local)

Pour une utilisation en local, sans dépendre d'une connexion Internet pour l'analyse de texte :

1.  **Installez Ollama** : Suivez les instructions sur [ollama.ai](https://ollama.ai/) pour l'installer sur votre système.
2.  **Téléchargez un modèle** : Choisissez un modèle adapté à vos besoins (par exemple, `llama2`, `mistral`).
    ```bash
    ollama pull mistral
    ```
3.  **Configurez l'outil** : Assurez-vous que vos scripts (par exemple `qa_service.py`) sont configurés pour utiliser Ollama comme fournisseur de modèle.

### Utilisation avec les API (Gemini et OpenAI)

Pour utiliser des modèles plus puissants via leurs API :

1.  **Obtenez vos clés d'API** :
    *   **Gemini** : Créez un projet sur [Google AI Studio](https://aistudio.google.com/) et récupérez votre clé d'API.
    *   **OpenAI** : Accédez à votre compte sur [platform.openai.com](https://platform.openai.com/) et générez une clé d'API.
2.  **Configurez les variables d'environnement** : Pour des raisons de sécurité, ne codez pas vos clés en dur. Créez un fichier `.env` à la racine du projet et ajoutez-y vos clés :
    ```
    GEMINI_API_KEY="VOTRE_CLÉ_GEMINI"
    OPENAI_API_KEY="VOTRE_CLÉ_OPENAI"
    ```
3.  **Adaptez le code** : Modifiez les services correspondants (par exemple `qa_service.py`, `summarization_service.py`) pour qu'ils utilisent la bibliothèque du fournisseur d'API souhaité (par exemple, `google-generativeai` pour Gemini, `openai` pour OpenAI).

## 📂 Structure du Projet

```
.
├── data/                # Dossier pour placer vos fichiers à analyser
├── services/            # Contient la logique métier (transcription, QA, etc.)
├── download_model.py    # Script pour télécharger le modèle de langue
├── run.py               # Point d'entrée pour lancer l'application
├── requirements.txt     # Liste des dépendances Python
└── export.docx          # Fichier de sortie généré
```

## 📄 Licence

Ce projet est distribué sous la licence spécifiée dans le fichier `LICENSE.txt`.
