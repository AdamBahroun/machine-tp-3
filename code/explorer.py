# code/explorer.py : distribution des catégories
import csv, os
from collections import Counter

ICI = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(ICI, "..", "data", "tickets.csv"), encoding="utf-8") as f:
    lignes = list(csv.DictReader(f))

for cat, n in Counter(l["categorie"] for l in lignes).most_common():
    print(f"{cat:<13}{n:>3} {100*n/len(lignes):>5.1f} % {'#' * n}")
print("\nTickets ambigus :", sum(int(l["ambigu"]) for l in lignes), "sur", len(lignes))
