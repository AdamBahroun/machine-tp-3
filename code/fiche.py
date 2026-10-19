# code/fiche.py : génère resultats/fiche_decision.md à partir des JSON de resultats/
import glob, json, os

ICI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(ICI, "..", "resultats")
PAUSE = 2.1  # pause incluse dans duree_s : on la retire pour estimer la latence

tous = []
for p in sorted(glob.glob(os.path.join(RES, "*.json"))):
    with open(p, encoding="utf-8") as f:
        tous.append(json.load(f))
base = sorted([r for r in tous if r["etiquette"] == r["modele"]],
              key=lambda r: r["macro_f1"], reverse=True)
variantes = [r for r in tous if r["etiquette"] != r["modele"]]
if len(base) < 2:
    raise SystemExit("Il faut au moins 2 modèles évalués dans resultats/")


def latence(r):
    n = len(r["ids"])
    return max(0.001, (r["duree_s"] - PAUSE * n) / n)


meilleur, second = base[0], base[1]
ecart_t = abs(meilleur["n_corrects"] - second["n_corrects"])
ecart_pts = 100 * (meilleur["macro_f1"] - second["macro_f1"])

retenu, motif = meilleur, "meilleur macro-F1"
proches = [r for r in base if abs(r["n_corrects"] - meilleur["n_corrects"]) < 5]
rapides = [r for r in proches if latence(r) * 5 <= latence(meilleur)]
if rapides:
    retenu = min(rapides, key=latence)
    motif = "écart < 5 tickets avec le meilleur et latence au moins 5x plus faible"
elif ecart_t < 5:
    motif = "meilleur macro-F1, mais écart < 5 tickets : pas de différence mesurable"

faible = min(retenu["scores"].items(), key=lambda kv: kv[1]["f1"])
confusions = sorted(((v, p, c) for v, ligne in retenu["matrice"].items()
                     for p, c in ligne.items() if p != v and c > 0),
                    key=lambda t: -t[2])[:3]

L = []
L.append("# Fiche de décision : choix d'un modèle pour le tri de tickets\n")
L.append("## Tableau comparatif\n")
L.append("| Modèle | accuracy | macro-F1 | corrects | Écart (tickets) | Durée (s) |")
L.append("|---|---|---|---|---|---|")
for r in base + variantes:
    L.append(f"| {r['etiquette']} | {r['accuracy']:.3f} | {r['macro_f1']:.3f} | "
             f"{r['n_corrects']} | {r['n_corrects'] - meilleur['n_corrects']:+d} | {r['duree_s']} |")
L.append("\n## Fiche\n")
L.append("| Rubrique | Contenu |")
L.append("|---|---|")
L.append("| Tâche et jeu de test | Router les tickets vers 4 équipes ; 72 tickets annotés, classes déséquilibrées |")
L.append("| Métrique de décision | macro-F1, choisie avant de voir les résultats |")
L.append("| Candidats évalués | " + ", ".join(r["modele"] for r in base) + " |")
L.append(f"| Modèle retenu et son score | {retenu['modele']} : macro-F1 {retenu['macro_f1']:.3f}, "
         f"accuracy {retenu['accuracy']:.3f}, {retenu['n_corrects']}/{len(retenu['ids'])} corrects ({motif}) |")
L.append(f"| Écart avec le deuxième | {meilleur['modele']} vs {second['modele']} : "
         f"{ecart_pts:.1f} points de macro-F1 ET {ecart_t} ticket(s) "
         f"({'différence mesurable' if ecart_t >= 5 else 'pas de différence mesurable, seuil = 5 tickets'}) |")
L.append(f"| Catégorie la plus faible | {faible[0]} (F1 {faible[1]['f1']:.3f}, "
         f"precision {faible[1]['precision']:.3f}, recall {faible[1]['recall']:.3f}) |")
L.append(f"| Latence | environ {latence(retenu):.2f} s par ticket (durée totale {retenu['duree_s']} s, pause de 2,1 s par ticket déduite) |")
risque = f"taux d'invalides {retenu['taux_invalides']:.3f}"
if confusions:
    v, p, c = confusions[0]
    risque += f" ; confusion la plus fréquente : {v} classé {p} ({c} ticket(s))"
L.append(f"| Risque identifié | {risque} |")

L.append("\n## Confusion matrix : erreurs les plus fréquentes du modèle retenu\n")
if confusions:
    for v, p, c in confusions:
        L.append(f"- {v} -> {p} : {c} ticket(s)")
else:
    L.append("- aucune erreur")
L.append("\nExplication : À COMPLÉTER (pourquoi le modèle confond ces catégories, en citant des tickets de comparer.py).")

L.append("\n## Effet de la consigne (4 exemples)\n")
var = next((r for r in variantes if r["modele"] == meilleur["modele"]),
           variantes[0] if variantes else None)
if var:
    ref = next(r for r in base if r["modele"] == var["modele"])
    gain_t = var["n_corrects"] - ref["n_corrects"]
    gain_pts = 100 * (var["macro_f1"] - ref["macro_f1"])
    L.append(f"- {var['modele']} : {ref['macro_f1']:.3f} -> {var['macro_f1']:.3f} avec exemples "
             f"({gain_pts:+.1f} points, {gain_t:+d} ticket(s))")
    L.append(f"- Écart entre modèles : {ecart_t} ticket(s). "
             + ("Le gain des exemples dépasse cet écart : le choix du modèle n'était pas le levier principal."
                if gain_t > ecart_t else
                "Le gain des exemples ne dépasse pas l'écart entre modèles."))
else:
    L.append("- variante non évaluée")

texte = "\n".join(L) + "\n"
with open(os.path.join(RES, "fiche_decision.md"), "w", encoding="utf-8") as f:
    f.write(texte)
print(texte)
