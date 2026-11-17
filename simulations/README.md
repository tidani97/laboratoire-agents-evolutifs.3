

# CDI-01 — Moteur de simulation

## 1. Présentation

Le fichier `cdi_01.py` contient le premier moteur de simulation du laboratoire des agents évolutifs.

Il permet de comparer trois formes d'organisation collective entre agents spécialisés.

## 2. Prérequis

Le programme nécessite :

- Python 3.10 ou supérieur.

- Aucune bibliothèque externe.

- Un environnement capable d'exécuter des scripts Python.

Les bibliothèques utilisées appartiennent à Python :

- random

- csv

- pathlib

- collections

## 3. Structure des agents

Le moteur initialise trois agents :

- Explorateur : spécialisé en observation.

- Analyste : spécialisé en analyse.

- Constructeur : spécialisé en construction.

Chaque agent possède des compétences et une contribution individuelle.

## 4. Conditions simulées

Le programme compare :

1. Isolement.

2. Communication temporaire.

3. Mémoire partagée.

## 5. Environnements

Les missions sont réparties entre cinq environnements :

- Abondant.

- Rare.

- Dispersé.

- Instable.

- Mixte.

## 6. Lancement

Depuis la racine du dépôt, exécuter :

```bash

python simulations/cdi_01.py

```

Le programme réalise 1 800 missions simulées.

## 7. Résultats générés

Deux fichiers CSV sont produits automatiquement :

`results/cdi_01_runs.csv`

Contient les résultats détaillés de chaque mission.

`results/cdi_01_summary.csv`

Contient les moyennes regroupées par condition et environnement.

Le dossier `results` est créé automatiquement lors de l'exécution.

## 8. Limites du moteur actuel

CDI-01 est un modèle exploratoire simplifié.

Les agents ne disposent pas encore d'une véritable évolution génétique.

Les compétences initiales restent fixes.

Les mécanismes de mémoire et de communication sont représentés par des règles mathématiques simplifiées.

Les résultats dépendent donc directement des hypothèses inscrites dans le programme.

## 9. Évolutions prévues

CDI-02 :

Introduction d'une mémoire individuelle et d'un apprentissage par expérience.

CDI-03 :

Introduction des mutations des compétences.

CDI-04 :

Introduction de la sélection et de la reproduction.

CDI-05 :

Transmission des caractéristiques entre générations.

CDI-06 :

Étude de l'émergence de stratégies collectives.

## 10. Principe de recherche

Chaque évolution du moteur doit pouvoir être comparée à une version précédente.

Les paramètres, les résultats et les conditions expérimentales doivent rester documentés afin de préserver la reproductibilité des expériences.

```

### Étape 3 — Enregistrer

Message de validation :

`Documentation du moteur de simulation CDI-01`

Puis confirme avec **Commit changes**.

<badge color="success">Objectif suivant</badge>

Après ça, nous aurons les six fichiers de notre première architecture documentaire et technique.

Et je te proposerai de vérifier le dépôt avant de construire CDI-02. Cette fois, nous allons donner à nos agents une mémoire qui leur permettra réellement d'apprendre de leurs expériences. 🧬