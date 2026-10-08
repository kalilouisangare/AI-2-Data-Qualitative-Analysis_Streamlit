# Projet d'Analyse Qualitative Automatisée

Cet outil permet de réaliser une analyse qualitative complète sur des documents texte ou des fichiers audio. Il automatise les tâches de transcription, traduction, résumé, et permet de poser des questions directement sur le contenu de vos documents.

**Architecture** : backend **FastAPI** (API, port 8000) + interface web **Streamlit** (port 8501).

## ✨ Fonctionnalités

- **Transcription Audio** : Convertit les fichiers audio en texte.
- **Traduction** : Traduit le contenu textuel dans la langue de votre choix.
- **Résumé Automatique** : Génère des résumés concis de longs documents.
- **Questions & Réponses (QA)** : Obtenez des réponses précises à vos questions basées sur les documents fournis.
- **Synthèse Vocale (TTS)** : Convertit le texte des résultats en fichier audio.

## 🚀 Installation

### 1. Prérequis
- [Python 3.8+](https://www.python.org/)
- [Git](https://git-scm.com/)

### 2. Cloner le dépôt
```bash
git clone https://github.com/kalilouisangare/AI-2-Data-Qualitative-Analysis_Streamlit
cd AI-2-Data-Qualitative-Analysis_Streamlit
```

### 3. Créer et activer l'environnement virtuel
- **Windows** :
```bash
python -m venv venv
.\venv\Scripts\activate
```
- **macOS / Linux** :
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Installer les dépendances
```bash
pip install -r requirements_streamlit.txt
```

### 5. Configurer les clés API
```bash
cp .env.exemple .env
```
Puis renseignez vos clés dans `.env` (jamais versionné, voir `.gitignore`).

## 📖 Lancement

```bash
python run_streamlit.py
```

Ce script démarre :
1. le **backend FastAPI** sur [http://127.0.0.1:8000](http://127.0.0.1:8000) (API)
2. l'**interface Streamlit** sur [http://localhost:8501](http://localhost:8501) — ouvrez cette adresse dans votre navigateur

## 🔧 Configuration des modèles

Outil configurable avec des LLM **locaux via Ollama** (usage hors ligne) ou des **API externes** (Gemini, OpenAI).

### Ollama (local, sans Internet)
1. Installez Ollama sur [ollama.ai](https://ollama.ai/)
2. Téléchargez un modèle : `ollama pull mistral`
3. Sélectionnez Ollama comme fournisseur dans la configuration

### API (Gemini / OpenAI)
1. Récupérez votre clé ([Google AI Studio](https://aistudio.google.com/) ou [platform.openai.com](https://platform.openai.com/))
2. Complétez le fichier `.env` :
```
GEMINI_API_KEY="VOTRE_CLÉ_GEMINI"
OPENAI_API_KEY="VOTRE_CLÉ_OPENAI"
```
3. Les services concernés se trouvent dans le dossier `services/`

## 📂 Structure du projet
```
.
├── backend.py               # Application FastAPI (API, port 8000)
├── main_streamlit.py        # Interface Streamlit (port 8501)
├── run_streamlit.py         # Point d'entrée : lance FastAPI + Streamlit
├── backend_streamlit.py     # Logique de l'interface
├── utils_streamlit.py       # Utilitaires
├── services/                # Logique métier (transcription, QA, résumé…)
├── assets/                  # Ressources
├── requirements_streamlit.txt
├── .env.exemple             # Modèle de configuration des clés
└── LICENSE.txt
```

## 📄 Licence

Ce projet est distribué sous la licence MIT (voir `LICENSE.txt`).
