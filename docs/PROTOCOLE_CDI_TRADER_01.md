

# PROTOCOLE EXPERIMENTAL CDI-TRADER 01

## 1. Objectif

Développer un système expérimental multi-agents capable d'analyser les marchés financiers, de proposer des transactions, de prendre des décisions collectives et d'apprendre à partir des résultats.

Le système doit privilégier la protection du capital avant la recherche de profit.

## 2. Capital expérimental

- Capital virtuel initial : 50 USD.

- Un portefeuille collectif partagé.

- Aucun capital réel engagé.

- Aucun ordre réel autorisé dans cette version.

## 3. Organisation des agents

### Agent 1 : Analyste technique

Responsabilités :

- Identifier les tendances.

- Étudier les chandeliers.

- Identifier les supports et résistances.

- Étudier les indicateurs techniques.

- Proposer achat, vente ou abstention.

### Agent 2 : Analyste économique

Responsabilités :

- Étudier les événements économiques.

- Surveiller les annonces importantes.

- Évaluer la volatilité.

- Identifier les risques macroéconomiques.

- Proposer achat, vente ou abstention.

### Agent 3 : Gestionnaire du risque

Responsabilités :

- Surveiller le capital.

- Calculer les pertes potentielles.

- Contrôler l'exposition.

- Vérifier les limites de risque.

- Refuser toute transaction dangereuse.

Le gestionnaire du risque possède un droit de veto.

### Agent 4 : Décisionnaire

Responsabilités :

- Recevoir les propositions des autres agents.

- Comparer les analyses.

- Évaluer les arguments.

- Prendre la décision finale.

- Valider ou refuser chaque transaction.

Seul cet agent possède le pouvoir de validation.

## 4. Règles décisionnelles

Chaque agent peut proposer une transaction.

Le décisionnaire doit examiner :

- La proposition technique.

- La proposition économique.

- La proposition du gestionnaire du risque.

- Sa propre analyse.

Une transaction ne peut être autorisée que si :

- Les conditions minimales de validation sont réunies.

- Le gestionnaire du risque ne pose pas son veto.

- Le capital disponible est suffisant.

- Les limites expérimentales sont respectées.

L'abstention est une décision parfaitement acceptable.

## 5. Gestion du risque

Paramètres initiaux expérimentaux :

- Risque théorique maximal par transaction : 1 % du capital.

- Drawdown maximal expérimental : 10 %.

- Interdiction de poursuivre les transactions après déclenchement du seuil d'arrêt.

- Stop-loss obligatoire dans les futurs tests sur données réelles.

- Journalisation de toutes les décisions.

Ces paramètres devront être testés et réévalués.

## 6. Apprentissage collectif

Chaque décision doit être enregistrée.

Les agents doivent pouvoir :

- Comparer leurs propositions aux résultats.

- Identifier les erreurs.

- Mesurer la qualité de leurs analyses.

- Adapter leurs méthodes.

- Conserver les expériences utiles.

L'apprentissage ne doit jamais permettre de contourner les règles de sécurité.

## 7. Environnements expérimentaux

Les tests doivent couvrir :

1. Marché haussier.

2. Marché baissier.

3. Marché latéral.

4. Forte volatilité.

5. Faible volatilité.

Les simulations doivent être répétées avec plusieurs graines aléatoires afin de comparer les résultats.

## 8. Indicateurs de performance

Mesurer :

- Capital final.

- Nombre de transactions.

- Taux de réussite.

- Pertes cumulées.

- Drawdown maximal.

- Nombre de transactions refusées.

- Qualité des propositions.

- Évolution des compétences des agents.

Une rentabilité ponctuelle ne constitue pas une preuve de fiabilité.

## 9. Intégration MetaTrader 5

L'intégration se fera progressivement :

Phase A : lecture des données historiques.

Phase B : analyse des cotations et des marchés.

Phase C : backtesting avec coûts de transaction.

Phase D : compte démo et ordres fictifs.

Phase E : évaluation indépendante avant toute éventuelle autorisation réelle.

Aucun identifiant, mot de passe ou secret de connexion ne doit être enregistré dans GitHub.

## 10. Conditions avant le trading réel

Le passage au trading réel nécessitera :

- Des tests historiques suffisamment nombreux.

- Des résultats reproductibles.

- Une validation en compte démo.

- Une gestion du risque vérifiée.

- Une surveillance humaine.

- Une autorisation explicite du propriétaire du compte.

- Un mécanisme d'arrêt d'urgence.

Aucun agent ne peut autoriser seul le passage au trading réel.

## 11. Principe fondamental

La priorité de CDI-TRADER n'est pas de réaliser le maximum de transactions.

Sa priorité est de prendre des décisions justifiées, de protéger le capital, d'apprendre de ses erreurs et de savoir s'abstenir lorsque les conditions sont défavorables.

---

Fin du protocole CDI-TRADER 01.