
---

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
git clone <URL_DU_DEPOT>
cd analyse_qualitative
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

1.  **Ajouter vos données** : Placez tous vos fichiers (par exemple `.wav`, `.mp3`, `.txt`, `.docx`) dans le dossier `data/`.
2.  **Lancer l'analyse** : Exécutez le script principal pour démarrer le traitement.
    ```bash
    python run.py
    ```
3.  **Consulter les résultats** : Une fois l'analyse terminée, les résultats seront compilés dans le fichier `export.docx`.

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


---
