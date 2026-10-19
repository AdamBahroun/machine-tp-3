# code/comparer.py : tableau comparatif + tickets sur lesquels les modèles divergent
import csv, glob, json, os

ICI = os.path.dirname(os.path.abspath(__file__))
res = []
for chemin in sorted(glob.glob(os.path.join(ICI, "..", "resultats", "*.json"))):
    with open(chemin, encoding="utf-8") as f:
        res.append(json.load(f))
if not res:
    raise SystemExit("Aucun résultat dans resultats/")

with open(os.path.join(ICI, "..", "data", "tickets.csv"), encoding="utf-8") as f:
    textes = {l["id"]: l for l in csv.DictReader(f)}

res.sort(key=lambda r: r["macro_f1"], reverse=True)
meilleur = res[0]["n_corrects"]
print(f"{'Modèle':<34}{'accuracy':>9}{'macro-F1':>9}{'corrects':>9}{'écart(tickets)':>15}{'durée(s)':>9}")
for r in res:
    ecart = r["n_corrects"] - meilleur
    print(f"{r['etiquette']:<34}{r['accuracy']:>9.3f}{r['macro_f1']:>9.3f}"
          f"{r['n_corrects']:>9}{ecart:>15}{r['duree_s']:>9}")
print("\nRègle : écart >= 5 tickets (~7 points de macro-F1) pour parler de différence.")

print("\n--- Tickets avec désaccord entre candidats ---")
ids = res[0]["ids"]
n = 0
for i, tid in enumerate(ids):
    preds = {r["etiquette"]: r["predits"][i] for r in res}
    if len(set(preds.values())) > 1:
        n += 1
        t = textes[tid]
        print(f"\n{tid} [réf: {t['categorie']}{' | AMBIGU' if t['ambigu']=='1' else ''}] {t['texte']}")
        for k, v in preds.items():
            print(f"    {'OK ' if v == t['categorie'] else 'XX '}{k}: {v}")
print(f"\n{n} tickets avec désaccord sur {len(ids)}.")
