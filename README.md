# BottleNeck — Pipeline automatisé de transformation et d'analyse de données

## Présentation

Ce projet a été réalisé dans le cadre de ma formation **Data Engineer chez OpenClassrooms**.

L'objectif est d'automatiser le traitement des données commerciales de BottleNeck, une entreprise spécialisée dans la vente de vins.

Le pipeline permet de nettoyer et rapprocher plusieurs sources de données, de calculer le chiffre d'affaires, d'identifier les vins premium à l'aide d'un Z-score et de produire des fichiers exploitables par les équipes métier.

L'ensemble des traitements est orchestré avec **Kestra**, dans un environnement **Docker**.

## Technologies utilisées

| Technologie | Utilisation |
|---|---|
| Python | Exécution des traitements, calcul statistique et exports |
| SQL | Nettoyage, transformation, jointure et agrégation |
| DuckDB | Moteur analytique SQL |
| Kestra | Orchestration, planification et gestion des erreurs |
| Docker Compose | Exécution des services PostgreSQL et Kestra |
| PostgreSQL | Base de données interne de Kestra |
| Pandas | Manipulation des données |
| OpenPyXL / xlwt | Lecture et génération de fichiers Excel |

## Architecture du pipeline

Le pipeline suit les étapes suivantes :

1. Lecture des sources Excel ERP, liaison et Web.
2. Nettoyage des données avec SQL et DuckDB.
3. Suppression des doublons Web.
4. Fusion des données ERP et Web via la table de liaison.
5. Calcul du chiffre d'affaires.
6. Calcul du Z-score pour identifier les vins premium.
7. Contrôle parallèle des extractions premium et ordinaires.
8. Export du rapport de chiffre d'affaires.
9. Vérification de la présence des trois fichiers finaux.

Kestra orchestre ces traitements et assure leur exécution selon un calendrier mensuel.

## Organisation du projet

```text
BottleNeck/
├── scripts/
│   ├── 00_run_sql.py
│   ├── 01_clean_erp.sql
│   ├── 02_clean_liaison.sql
│   ├── 03_clean_web.sql
│   ├── 04_merge_data.sql
│   ├── 05_calculate_revenue.sql
│   ├── 06_zscore.py
│   ├── 07_export_revenue.py
│   └── 08_tests.py
├── flows/
│   └── bottleneck_workflow.yml
├── data/                         # Sources locales non publiées
├── output/                       # Résultats générés non publiés
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
├── Data_Lineage_BottleNeck.drawio
├── Data_Lineage_BottleNeck.drawio.png
└── README.md
```

Les dossiers `data/` et `output/` sont créés localement. Leur contenu n'est pas inclus dans le dépôt public.

## Installation

### Prérequis

- Git
- Python 3
- Docker Desktop et Docker Compose
- Les trois fichiers sources BottleNeck

### 1. Cloner le dépôt

```bash
git clone https://github.com/Fatima012020/BottleNeck-Data-Pipeline.git
cd BottleNeck-Data-Pipeline
```

### 2. Installer les dépendances Python

Créer un environnement virtuel :

```bash
python -m venv .venv
```

Sous Windows PowerShell :

```powershell
.\.venv\Scripts\Activate.ps1
```

Installer les bibliothèques :

```bash
python -m pip install -r requirements.txt
```

### 3. Préparer les données

Créer les dossiers nécessaires :

```powershell
New-Item -ItemType Directory -Force data, output
```

Placer dans `data/` :

- `erp.xlsx`
- `liaison.xlsx`
- `web.xlsx`

Les fichiers sources ne sont pas distribués dans le dépôt public.

### 4. Configurer Docker

Créer un fichier `.env` à partir de `.env.example` et renseigner un mot de passe PostgreSQL local.

Sous PowerShell :

```powershell
Copy-Item .env.example .env
```

Modifier ensuite la valeur `POSTGRES_PASSWORD` dans `.env`.

Ne jamais publier le fichier `.env`.

### 5. Démarrer les services

```bash
docker compose config --quiet
docker compose up -d
docker compose ps
```

L'interface Kestra est accessible à l'adresse :

http://localhost:8080

### 6. Importer le workflow Kestra

Dans l'interface Kestra, importer le fichier :

`flows/bottleneck_workflow.yml`

Le workflow appartient au namespace `bottleneck.data` et porte l'identifiant `bottleneck_workflow`.

Lancer ensuite une exécution manuelle depuis Kestra.

## Exécution des traitements

Le script `scripts/00_run_sql.py` exécute successivement les cinq fichiers SQL :

- `01_clean_erp.sql`
- `02_clean_liaison.sql`
- `03_clean_web.sql`
- `04_merge_data.sql`
- `05_calculate_revenue.sql`

Les résultats intermédiaires sont enregistrés dans la base locale `output/bottleneck.duckdb`.

Le script `06_zscore.py` réalise l'analyse statistique et produit les extractions de vins.

Le script `07_export_revenue.py` génère le rapport Excel du chiffre d'affaires.

Le script `08_tests.py` contient les contrôles de validation du pipeline.

## Orchestration et automatisation

Le workflow Kestra comprend :

- L'exécution des transformations SQL.
- Le calcul du Z-score.
- Deux contrôles d'extractions exécutés en parallèle.
- La génération du rapport de chiffre d'affaires.
- Un contrôle final des trois livrables.
- Un bloc de journalisation des erreurs.

Les principales tâches de transformation disposent d'une politique de relance configurée avec un maximum de trois tentatives et un intervalle de dix secondes.

La planification utilise l'expression cron :

`0 9 15 * *`

Elle correspond à une exécution le **15 de chaque mois à 9 h**, dans le fuseau horaire `Europe/Paris`, lorsque le planificateur Kestra est actif.

## Résultats obtenus

| Indicateur | Résultat |
|---|---:|
| Produits ERP | 825 |
| Produits Web après dédoublonnage | 714 |
| Produits fusionnés | 714 |
| Chiffre d'affaires total | 70 568,60 € |
| Vins premium identifiés | 30 |
| Tests de validation | 7/7 réussis |

Les résultats correspondent à l'exécution validée du projet sur le jeu de données BottleNeck.

## Fichiers générés

Le pipeline produit les livrables suivants dans le dossier `output/` :

| Fichier | Contenu |
|---|---|
| `bottleneck.duckdb` | Base analytique intermédiaire |
| `vins_premium.csv` | Sélection des vins premium |
| `vins_ordinaires.csv` | Sélection des vins ordinaires |
| `rapport_chiffre_affaires.xls` | Rapport de chiffre d'affaires |

## Qualité et fiabilité

La solution intègre plusieurs mécanismes de contrôle :

- Vérification des volumes de données après transformation.
- Tests de cohérence des données et des résultats.
- Vérification des fichiers générés.
- Relances automatiques sur certaines tâches.
- Journalisation des erreurs dans Kestra.

Une exécution du workflow a été confirmée avec l'état `SUCCESS` en environ 9,5 secondes.

## Sécurité et limites

Les fichiers sources, les résultats générés, la base DuckDB locale et les secrets d'environnement sont exclus du dépôt GitHub.

Le workflow utilise actuellement un exécuteur de processus local et installe certaines dépendances Python au démarrage des traitements. Pour une utilisation en production, il serait préférable de disposer d'une image d'exécution versionnée, de limiter les privilèges des conteneurs et d'utiliser une gestion dédiée des secrets.

Le fonctionnement dépend également de la disponibilité des fichiers sources et de la bonne configuration de Kestra et PostgreSQL.

## Compétences mises en pratique

- Développement de pipelines de données avec Python et SQL.
- Nettoyage, dédoublonnage et rapprochement de données.
- Analyse statistique et calcul d'indicateurs métier.
- Automatisation de traitements avec Kestra.
- Conteneurisation avec Docker Compose.
- Mise en place de contrôles qualité et de mécanismes de reprise.
- Documentation et reproductibilité d'un projet Data Engineering.

---

**Projet réalisé dans le cadre du parcours Data Engineer — OpenClassrooms.**