

# CDI-01 — Protocole expérimental

## 1. Objectif

Étudier comment des agents autonomes aux compétences différentes peuvent coopérer, communiquer et s'adapter à plusieurs environnements.

L'expérience cherche à comparer trois organisations :

1. Agents isolés, sans communication.

2. Communication temporaire entre agents.

3. Mémoire partagée permanente.

## 2. Population initiale

Trois agents sont créés avec des compétences spécialisées.

| Agent | Observation | Analyse | Construction |

|---|---:|---:|---:|

| Explorateur | 90 | 25 | 20 |

| Analyste | 25 | 90 | 25 |

| Constructeur | 20 | 25 | 90 |

Les différences de compétences doivent encourager la complémentarité et l'entraide.

## 3. Environnements

Les agents seront confrontés à cinq environnements :

- Abondant : ressources facilement accessibles.

- Rare : ressources limitées.

- Dispersé : ressources éloignées les unes des autres.

- Instable : conditions susceptibles de changer.

- Mixte : combinaison de plusieurs difficultés.

## 4. Organisation des expériences

Paramètres initiaux :

- 20 graines aléatoires.

- 30 missions par condition.

- 30 tours par mission.

- 3 conditions expérimentales.

Total : 1 800 missions.

Les 15 premières missions utilisent un environnement mixte.

Les 15 suivantes explorent les différents environnements.

## 5. Indicateurs mesurés

Pour chaque mission, nous enregistrons :

- Score collectif.

- Nombre de tours réussis.

- Connaissances finales.

- Contribution individuelle de chaque agent.

- Environnement testé.

- Condition de communication.

## 6. Hypothèses

H1 : La communication temporaire améliore la coordination.

H2 : La mémoire partagée facilite l'accumulation des connaissances.

H3 : Les compétences complémentaires permettent une meilleure adaptation collective.

H4 : L'organisation la plus performante dépend de l'environnement.

## 7. Limites

CDI-01 est un modèle exploratoire simplifié.

Les résultats ne constituent pas une preuve scientifique du comportement d'agents réels.

Cette première version ne met pas encore en œuvre de véritable mutation génétique ni de sélection évolutive.

## 8. Étapes futures

- CDI-02 : introduire la mémoire individuelle évolutive.

- CDI-03 : introduire la mutation des compétences.

- CDI-04 : introduire la sélection et la reproduction.

- CDI-05 : étudier la coopération entre générations.

- CDI-06 : comparer les stratégies dans des environnements combinés.

## 9. Principe directeur

L'objectif n'est pas uniquement de déterminer quel agent est le plus performant.

Il s'agit de comprendre dans quelles conditions des individus différents peuvent construire ensemble un système plus efficace que leurs capacités individuelles.