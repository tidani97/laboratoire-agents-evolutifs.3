

# CDI-02 — Protocole d'apprentissage et de trading expérimental

## 1. Objectif général

CDI-02 introduit l'apprentissage individuel et collectif des agents autonomes.

L'objectif est d'observer comment les agents peuvent améliorer leurs décisions grâce à leurs expériences, leurs réussites et leurs erreurs.

Une branche complémentaire, CDI-TRADER, étudiera l'analyse des marchés financiers.

## 2. Apprentissage individuel

Chaque agent possède :

- Une mémoire personnelle.

- Un historique de ses décisions.

- Un système d'évaluation des résultats.

- Une capacité d'adaptation progressive.

Les agents doivent pouvoir modifier leurs stratégies sans perdre leur identité initiale.

## 3. Apprentissage collectif

Trois configurations seront comparées :

- Agents isolés.

- Communication temporaire.

- Mémoire partagée.

L'objectif est de mesurer les avantages et les limites de chaque organisation.

## 4. Module CDI-TRADER

### Objectif

Étudier la capacité d'agents spécialisés à analyser les marchés financiers et à élaborer des stratégies de trading simulées.

### Agent 1 — Analyste technique

Responsabilités :

- Identifier les tendances.

- Repérer les supports et résistances.

- Étudier les figures graphiques.

- Analyser les volumes.

- Comparer plusieurs unités de temps.

### Agent 2 — Analyste économique

Responsabilités :

- Étudier les événements économiques.

- Observer les décisions des banques centrales.

- Analyser l'influence des actualités.

- Étudier les variations de volatilité.

- Identifier les risques liés aux annonces économiques.

### Agent 3 — Gestionnaire des risques

Responsabilités :

- Calculer le risque par position.

- Étudier les stop-loss.

- Mesurer les pertes maximales.

- Évaluer le rapport rendement/risque.

- Éviter les expositions excessives.

### Agent 4 — Trader décisionnaire

Responsabilités :

- Comparer les analyses des autres agents.

- Identifier les opportunités.

- Proposer une entrée, une sortie ou une absence de position.

- Justifier chaque décision.

- Enregistrer les résultats pour apprentissage futur.

## 5. Intégration de MetaTrader 5

MetaTrader 5 sera étudié comme plateforme de collecte de données et d'expérimentation.

Fonctionnalités envisagées :

- Importation des historiques de prix.

- Observation des cotations.

- Analyse des chandeliers.

- Étude des indicateurs techniques.

- Comparaison des unités de temps.

- Exportation des résultats de simulation.

Une future interface Python pourra exploiter l'API MetaTrader 5.

L'intégration devra commencer en lecture seule et utiliser un compte de démonstration pour les essais de stratégie.

Aucun identifiant, mot de passe ou secret de connexion ne devra être enregistré dans GitHub.

## 6. Environnements de marché

Les agents devront étudier plusieurs configurations :

- Marché haussier.

- Marché baissier.

- Marché latéral.

- Forte volatilité.

- Faible volatilité.

- Changement brutal de tendance.

Les actifs pourront inclure :

- Bitcoin.

- Ethereum.

- Or.

- Paires de devises.

## 7. Gestion du risque

La priorité absolue est la limitation des pertes.

Chaque stratégie devra intégrer :

- Un stop-loss théorique.

- Une taille de position calculée.

- Un risque maximal prédéfini.

- Une mesure du drawdown.

- Une comparaison entre gains et pertes.

- Une règle d'arrêt en cas de comportement anormal.

Aucun apprentissage ne devra être considéré comme une preuve de rentabilité future.

## 8. Évaluation des stratégies

Les indicateurs étudiés seront :

- Taux de réussite.

- Profit factor.

- Rendement moyen.

- Perte moyenne.

- Drawdown maximal.

- Nombre de positions.

- Résultat net après frais et spread.

Les stratégies devront être testées sur des données différentes de celles utilisées pour leur apprentissage afin de limiter le surapprentissage.

## 9. Sécurité expérimentale

Les premières expérimentations seront exclusivement réalisées en simulation ou en compte de démonstration.

Aucun ordre réel ne sera transmis automatiquement.

Toute évolution vers une utilisation réelle nécessitera une validation humaine indépendante et une nouvelle étude des risques.

## 10. Questions de recherche

- Un agent peut-il apprendre à reconnaître une tendance ?

- Peut-il distinguer un signal fiable d'un faux signal ?

- La coopération améliore-t-elle l'analyse ?

- La mémoire collective réduit-elle les erreurs répétées ?

- Un agent spécialisé dans le risque améliore-t-il la survie du système ?

- Les stratégies apprises restent-elles efficaces dans des marchés inconnus ?

## 11. Principe directeur

La performance ne sera jamais mesurée uniquement par les gains.

La capacité à préserver le capital, reconnaître ses erreurs et s'adapter aux changements du marché constitue un objectif central du laboratoire.