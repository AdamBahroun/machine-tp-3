# Fiche de décision : choix d'un modèle pour le tri de tickets

## Tableau comparatif

| Modèle | accuracy | macro-F1 | corrects | Écart (tickets) | Durée (s) |
|---|---|---|---|---|---|
| openai/gpt-oss-20b | 0.958 | 0.962 | 69 | +0 | 193.8 |
| qwen/qwen3.8-27b | 0.958 | 0.956 | 69 | +0 | 174.8 |
| openai/gpt-oss-120b | 0.931 | 0.933 | 67 | -2 | 206.5 |
| gpt-oss-20b + 4 exemples | 0.958 | 0.957 | 69 | +0 | 188.3 |

## Fiche

| Rubrique | Contenu |
|---|---|
| Tâche et jeu de test | Router les tickets vers 4 équipes ; 72 tickets annotés, classes déséquilibrées |
| Métrique de décision | macro-F1, choisie avant de voir les résultats |
| Candidats évalués | openai/gpt-oss-20b, qwen/qwen3.8-27b, openai/gpt-oss-120b |
| Modèle retenu et son score | openai/gpt-oss-20b : macro-F1 0.962, accuracy 0.958, 69/72 corrects (meilleur macro-F1, mais écart < 5 tickets : pas de différence mesurable) |
| Écart avec le deuxième | openai/gpt-oss-20b vs qwen/qwen3.8-27b : 0.6 points de macro-F1 ET 0 ticket(s) (pas de différence mesurable, seuil = 5 tickets) |
| Catégorie la plus faible | commercial (F1 0.929, precision 0.929, recall 0.929) |
| Latence | environ 0.59 s par ticket (durée totale 193.8 s, pause de 2,1 s par ticket déduite) |
| Risque identifié | taux d'invalides 0.014 ; confusion la plus fréquente : facturation classé commercial (1 ticket(s)) |

## Confusion matrix : erreurs les plus fréquentes du modèle retenu

- facturation -> commercial : 1 ticket(s)
- compte -> technique : 1 ticket(s)
- commercial -> invalide : 1 ticket(s)

Explication : À COMPLÉTER (pourquoi le modèle confond ces catégories, en citant des tickets de comparer.py).

## Effet de la consigne (4 exemples)

- openai/gpt-oss-20b : 0.962 -> 0.957 avec exemples (-0.5 points, +0 ticket(s))
- Écart entre modèles : 0 ticket(s). Le gain des exemples ne dépasse pas l'écart entre modèles.
