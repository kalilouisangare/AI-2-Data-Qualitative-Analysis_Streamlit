---# Feuille de Route Stratégique et Technique

* **Projet** : Quali-IA : Plateforme d'Analyse Qualitative Intelligente
* **Auteur** : Kalilou I Sangare
* **Support** : l'IA Générative (Google Studio AI)
* **Version** : 1.0 - Version de Capitalisation
* **Date** : 27/08/2024

---

## 1.0 Introduction, Contexte et Public Cible

**Contexte de ce Document :** Ce document est la charte fondatrice et la mémoire technique du projet "Quali-IA". Il a été rédigé pour capitaliser sur l'expérience acquise durant le cycle de développement, depuis la conceptualisation jusqu'à la phase de production. Il ne s'agit pas d'un manuel utilisateur, mais d'un dossier stratégique qui expose les décisions architecturales, les défis techniques rencontrés et les solutions implémentées.

**Objectif :** Servir de référence pour toute évolution future de ce projet et de modèle pour la conception et la gestion de projets d'IA similaires. Il vise à assurer la continuité et la maintenabilité du projet sur le long terme.

### Public Cible :

* **Vous-même (dans le futur) et Développeurs Repreneurs :** Pour comprendre rapidement l'architecture, les choix technologiques et les leçons apprises.
* **Chefs de Projet Technique / DSI :** Pour évaluer la pertinence de la stack technologique, la méthodologie de développement et planifier les ressources pour des projets futurs.
* **Architectes Logiciels :** Pour analyser les décisions de conception (backend stateless, gestion de l'état côté client, architecture de services).

---

## 2.0 Phase 1 : Cadrage Stratégique et Validation de la Faisabilité (Durée estimée : 1-2 jours)

### 2.1 Définition du Besoin Fondamental ("Le Pourquoi")

* **Problématique Métier :** Dans des domaines comme le Suivi-Évaluation, les sciences sociales ou les études de marché, une grande partie des données les plus riches sont non structurées (entretiens, groupes de discussion, réponses textuelles ouvertes). Leur analyse est un processus manuel, long, coûteux, et sujet aux biais de l'analyste.
* **Solution Envisagée :** Créer un "assistant analyste" sous la forme d'une application de bureau. Cet outil doit agir comme un levier de productivité, non comme un remplaçant de l'expert. Il doit automatiser les tâches à faible valeur ajoutée (transcription, recherche de faits) pour libérer du temps pour l'analyse stratégique.

### 2.2 Choix de l'Architecture Technique Principale : Le Dilemme Local vs. Cloud

* **Option 1 : Inférence via API distante (ex: OpenAI, Google Cloud).**
    *Analogie :* Louer les services d'un traiteur expert. Rapide et de haute qualité, mais vous envoyez vos "ingrédients" (données) à l'extérieur et payez à chaque plat.
    *Avantages :* Accès aux modèles les plus puissants du marché, pas de maintenance matérielle.
    *Inconvénients :* Coûts récurrents, latence réseau, et surtout, **rupture de la chaîne de confidentialité des données**.
* **Option 2 : Inférence 100% Locale.**
    *Analogie :* Construire sa propre cuisine professionnelle. Investissement initial en matériel, mais contrôle total, confidentialité absolue et pas de coût par utilisation.
    *Avantages :* Confidentialité maximale, maîtrise des coûts, fonctionnement hors ligne possible, contrôle total sur les modèles.
    *Inconvénients :* Nécessite un matériel adéquat (GPU), installation plus complexe.
* **Décision Stratégique :** Adopter une architecture **hybride flexible**. Le cœur de l'application sera 100% local (Option 2) pour garantir la souveraineté des données. Cependant, l'interface offrira la possibilité d'appeler des API externes (Option 1).

### 2.3 Sélection de la Stack Technologique ("La Boîte à Outils")

* **Backend :** FastAPI (performance asynchrone, simplicité).
* **Frontend :** Gradio (prototypage rapide pour l'IA, gestion du streaming).
* **Moteur LLM Local :** Ollama (simplicité d'installation et de gestion des modèles).
* **Moteurs d'IA Spécifiques :** Bibliothèque `transformers` de Hugging Face (standard de l'industrie).
* **Gestion de l'Environnement :** Python 3.10 (compatibilité maximale) et `venv` (isolation des projets).

---

## 3.0 Phase 2 : Développement du Socle Applicatif (Durée estimée : 3-4 jours)

### 3.1 Mise en Place du Backend "Stateless"

* Création des endpoints FastAPI de base.
* **Leçon Apprise Fondamentale :** Éviter à tout prix les variables globales pour stocker l'état de l'utilisateur. Le backend doit être "stateless", traitant chaque requête de manière indépendante.

### 3.2 Gestion de l'État Côté Client

* **Action Clé :** Utilisation intensive du composant `gr.State` dans Gradio.
* **Justification :** C'est la solution robuste pour stocker les données de la session d'un utilisateur (comme le texte du document chargé) directement dans l'interface, sans surcharger le backend.

### 3.3 Implémentation des Services d'IA de Base

* **Service de Transcription (Audio -> Texte) :** Intégration de `openai/whisper-base`.
    *Défi Technique Relevé :* Dépendance au logiciel `ffmpeg`, nécessitant une documentation d'installation système.
* **Service de Résumé (Texte -> Texte) :** Intégration de `airKlizz/mt5-base-wikinewssum-french`.
    *Leçon Apprise (Qualité) :* La qualité d'un modèle brut est souvent médiocre. L'amélioration passe par l'**ingénierie de prompt** et le **réglage des paramètres de génération** (`num_beams`, `no_repeat_ngram_size`).

---

## 4.0 Phase 3 : Montée en Puissance et Fonctionnalités Avancées (Durée estimée : 4-6 jours)

### 4.1 Intégration Multi-Modèles (LLM)

* **Défi Technique :** Chaque famille de LLM (`llama`, `phi`) a un "template de prompt" différent.
* **Solution :** Implémentation de **prompts conditionnels** dans `qa_service.py` qui adaptent le format de la requête en fonction du modèle sélectionné.

### 4.2 Gestion des Documents Volumineux : La Stratégie "Map-Reduce"

* **Problématique :** Dépassement de la fenêtre de contexte des LLM.
* **Solution Implémentée :**
    *Étape 1 (Map) :* Découpage du texte en "chunks" et résumé de chaque chunk avec un modèle spécialisé rapide.
    *Étape 2 (Reduce) :* Synthèse finale de tous les résumés partiels par un LLM puissant.

### 4.3 Visualisation et Analyse Sémantique

* **Technologie :** Utilisation de `spacy` pour le prétraitement sémantique (lemmatisation, suppression des mots vides), rendant le nuage de mots beaucoup plus pertinent.
* **Personnalisation :** L'interface permet à l'utilisateur de définir ses propres regroupements de synonymes.

### 4.4 Configurabilité et Déploiement

* **Problématique :** Comment un utilisateur non-technique peut-il gérer ses clés API ?
* **Solution :** Remplacement du fichier `.env` par un **onglet "Configuration"** qui sauvegarde les clés dans un fichier `config.json` local.
* **Objectif Final :** Packaging en `.exe` via **PyInstaller**, en considérant **Ollama comme une dépendance externe**.

---

---

# Manuel d'Utilisation de la Plateforme "Quali-IA"

* **Projet** : Quali-IA : Plateforme d'Analyse Qualitative Intelligente
* **Auteur** : Kalilou I Sangare
* **Support** : l'IA Générative (Google Studio AI)
* **Version** : 1.0
* **Date** : 27/08/2024

---

## 1.0 Introduction : Votre Assistant de Recherche Augmenté

**Contexte de ce Document :** Ce manuel est le **guide de prise en main officiel** de l'application "Outil d'Analyse Qualitative Intelligente". Il est conçu pour être non technique et orienté vers les cas d'usage métier.

**Objectif :** Permettre à tout utilisateur, quel que soit son niveau technique, de comprendre la valeur de chaque fonctionnalité et de l'utiliser de manière autonome et efficace.

### Public Cible :

* Analystes
* Chargés de Suivi-Évaluation
* Chercheurs
* Chefs de Projet
* Étudiants

### Analogie Clé : La Cuisine et le Grand Chef

* **Vos Données (fichiers Word, PDF, audio) :** Ce sont les ingrédients bruts.
* **L'Application "Quali-IA" :** C'est votre cuisine professionnelle, équipée d'appareils de pointe (les modèles d'IA).
* **Vous :** Vous êtes le Grand Chef. Votre rôle est de choisir les bons ingrédients et de donner les bonnes instructions.

**La Promesse Fondamentale : Confidentialité Totale.** Toute la "cuisine" se passe sur votre ordinateur. Vos données ne le quittent jamais.

---

## 2.0 Démarrage Rapide

### 2.1 Installation pour l'Administrateur

* **Prérequis :** Un ordinateur avec un GPU NVIDIA est fortement recommandé.
* **Installer Ollama :** Téléchargez et installez Ollama depuis `ollama.com`.
* **Télécharger les Modèles :** Ouvrez un terminal et tapez `ollama pull codellama` et `ollama pull phi4-mini-reasoning`.
* **Lancer l'Application :** Assurez-vous qu'Ollama tourne en arrière-plan, puis double-cliquez sur `AnalyseQualitative.exe`.

### 2.2 Démarrage pour l'Utilisateur

* **Lancez l'Application.** Une fenêtre de navigateur s'ouvrira.
* **Allez sur l'onglet "Étape 1 : Charger vos Données".**
* **Importez un Fichier.** L'application vous redirigera automatiquement vers l'Étape 2.

---

## 3.0 Guide des Outils d'Analyse (Étape 2)

Chaque sous-onglet de l'Étape 2 est un outil différent. Choisissez le bon pour votre besoin.

* **2.1 Résumé Automatique (Audio uniquement) :** Idéal pour un aperçu rapide d'un entretien.
* **2.2 Interrogation Standard (Q&A) :** Pour des questions factuelles. C'est un "Ctrl+F" intelligent. *Conseil :* `codellama` est excellent pour extraire des informations précises.
* **2.3 Analyse par Raisonnement :** Pour des questions ouvertes qui nécessitent une interprétation. *Conseil :* `phi4-mini-reasoning` est conçu pour cela et montrera son processus de pensée.
* **2.4 Analyse de Long Document :** Indispensable pour les documents de plus de 10-20 pages. Il découpe, analyse et synthétise.

---

## 4.0 Outils Complémentaires et Configuration

### 4.1 Visualisation : Le Nuage de Mots Sémantique

* **Objectif :** Obtenir une vue d'ensemble visuelle des concepts clés.
* **Astuce Pro : Le Regroupement de Synonymes.** Format : `mot_cible: synonyme1, synonyme2`.

### 4.2 Exporter vos Résultats

Sous chaque zone de résultat, vous trouverez des options pour exporter votre travail en `.txt`, `.docx`, ou `.csv`.

### 4.3 Configuration des API (Optionnel)

Si vous disposez de clés API, vous pouvez les ajouter dans l'onglet **"Configuration"**. Un redémarrage de l'application est nécessaire.

---

---

# Aide-Mémoire Technique du Développement (Post-Mortem)

* **Projet** : Quali-IA : Plateforme d'Analyse Qualitative Intelligente
* **Auteur** : Kalilou I Sangare
* **Support** : l'IA Générative (Google Studio AI)
* **Version** : 1.0
* **Date** : 27/08/2024

---

## 1.0 Introduction, Contexte et Public Cible

**Contexte de ce Document :** Ce document est un "post-mortem" technique, une analyse rétrospective des défis, des erreurs et des solutions découvertes pendant le développement du projet "Quali-IA".

**Objectif :** Servir de base de connaissances pour le débogage et la maintenance future, et de guide pragmatique pour éviter de refaire les mêmes erreurs.

### Public Cible :

* Développeurs
* Ingénieurs QA / Testeurs
* Étudiants et Développeurs Juniors en IA

---

## 2.0 Leçons Apprises et Règles d'Or

* **Leçon n°1 : La Stabilité de l'Environnement.**
    *Erreur :* GPU non détecté. *Règle d'or :* Toujours utiliser `venv` et installer `PyTorch` avec la commande CUDA explicite du site officiel.
* **Leçon n°2 : La Spécificité des Modèles.**
    *Erreur :* Modèles `phi4`/`deepseek` silencieux. *Règle d'or :* Adapter les "templates de prompt" pour chaque famille de modèles.
* **Leçon n°3 : Les Dépendances Cachées.**
    *Erreur :* Transcription échouant à cause de `ffmpeg` manquant. *Règle d'or :* Vérifier si une bibliothèque Python n'est pas un "wrapper" pour un logiciel système externe.
* **Leçon n°4 : La Gestion de l'État.**
    *Erreur :* Utilisation de variables globales dans le backend. *Règle d'or :* Concevoir un backend "stateless" et gérer l'état de la session dans le frontend avec `gr.State`.
* **Leçon n°5 : Le Défi du "Temps Réel".**
    *Erreur :* Interface utilisateur gelée. *Règle d'or :* Pour les tâches longues, le **streaming** est une nécessité pour le retour visuel.
* **Leçon n°6 : La Limite de la Fenêtre de Contexte.**
    *Erreur :* LLM plantant sur de longs documents. *Règle d'or :* Une stratégie de **découpage ("chunking")** et de **Map-Reduce** est obligatoire.
* **Leçon n°7 : La Volatilité des Modèles Communautaires.**
    *Erreur :* Modèles pour le bambara supprimés. *Règle d'or :* S'appuyer sur des modèles d'organisations établies (Meta, Google, etc.).
* **Leçon n°8 : Les Erreurs de Communication Client-Serveur (`422 Unprocessable Entity`).**
    *Erreur :* Spécifique à FastAPI. *Règle d'or :* Vérifier que les noms des paramètres du `payload` du client correspondent **exactement** à la signature de l'endpoint du serveur.

---

---

# Plan Générique pour la Reproduction de Projets d'IA Locaux

* **Projet** : Quali-IA : Plateforme d'Analyse Qualitative Intelligente
* **Auteur** : Kalilou I Sangare
* **Support** : l'IA Générative (Google Studio AI)
* **Version** : 1.0
* **Date** : 27/08/2024

---

## 1.0 Introduction, Contexte et Public Cible

**Contexte de ce Document :** Ce document est un **modèle de gestion de projet**, un plan d'action générique et reproductible, distillé à partir de l'expérience du projet "Quali-IA". Il se concentre sur la **méthodologie** et le séquencement des phases de développement.

**Objectif :** Fournir un cadre de travail structuré pour toute personne souhaitant lancer un projet similaire, de l'idée à la production.

### Public Cible :

* Chefs de Projet et Product Owners.
* Consultants et Indépendants.
* Vous-même, pour votre prochain projet d'IA.

---

## 2.0 Plan de Développement en 5 Phases

### Phase 1 : Conception et Cadrage (10% du temps)

* **Définir le Problème :** Quelle tâche manuelle cherche-t-on à automatiser ?
* **Choisir l'Architecture :** Locale (PyInstaller) ? Déploiement via Docker ? Web (Hugging Face Spaces) ?
* **Sélectionner la Stack Technologique :** FastAPI, Gradio, Ollama, etc.

### Phase 2 : Mise en Place de l'Environnement (5% du temps)

* **Isoler :** Toujours commencer par créer un environnement virtuel (`venv`).
* **Installer la Base :** Installer `PyTorch` en premier, avec la commande spécifique à CUDA.
* **Installer les Outils Externes :** Installer Ollama et télécharger les modèles de base.

### Phase 3 : Développement du Socle Applicatif (25% du temps)

* **Squelette Backend/Frontend :** Établir une communication "hello world".
* **Gestion de l'État :** Implémenter immédiatement le `gr.State` pour stocker le contexte.
* **Implémenter le Chargement de Fichiers :** C'est la première fonctionnalité essentielle.

---

## 3.0 Phases d'Implémentation et de Finalisation

### Phase 4 : Implémentation Itérative des Fonctionnalités (40% du temps)

* **Ajouter un Service à la Fois :** Ne pas tout faire en même temps. Ordre recommandé : Résumé -> Transcription -> Q&A -> Visualisation -> Analyse de Longs Documents.
* **Tester à Chaque Étape :** Lancer l'application après chaque ajout pour s'assurer de ne pas avoir introduit de régressions.

### Phase 5 : Finalisation et Déploiement (20% du temps)

* **Optimisation et Refactoring :** Peaufiner les prompts, nettoyer le code (ex: `utils.py`), améliorer la gestion des erreurs.
* **Préparation au Packaging :** Créer le script de lancement unique (`run.py`).
* **Construction de l'Exécutable :** Utiliser `PyInstaller` avec les bonnes options (`--add-data`, `--collect-all`).
* **Test Final :** Tester l'exécutable sur une machine "propre".
* **Rédaction de la Documentation :** Rédiger le manuel d'installation et d'utilisation.

---
