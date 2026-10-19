# code/evaluer.py : usage  python evaluer.py <modele>
import csv, json, os, sys, time
from classifieur import CONSIGNE, classer
from evaluation import afficher_rapport

PAUSE = 2.1  # 30 requêtes/minute au maximum
ICI = os.path.dirname(os.path.abspath(__file__))


def charger(chemin=os.path.join(ICI, "..", "data", "tickets.csv")):
    with open(chemin, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def evaluer(modele, lignes, consigne=CONSIGNE, etiquette=None, classeur=classer):
    etiquette = etiquette or modele
    vrais, predits, debut = [], [], time.time()
    for i, ligne in enumerate(lignes, 1):
        predits.append(classeur(ligne["texte"], modele, consigne=consigne))
        vrais.append(ligne["categorie"])
        print(f"\r{i}/{len(lignes)}", end="", flush=True)
        time.sleep(PAUSE)
    print()
    resume = afficher_rapport(etiquette, vrais, predits)
    resume.update(modele=modele, etiquette=etiquette,
                  duree_s=round(time.time() - debut, 1),
                  predits=predits, vrais=vrais, ids=[l["id"] for l in lignes])
    nom = etiquette.replace("/", "_").replace(" ", "_").replace("+", "plus")
    dossier = os.path.join(ICI, "..", "resultats")
    os.makedirs(dossier, exist_ok=True)
    with open(os.path.join(dossier, nom + ".json"), "w", encoding="utf-8") as f:
        json.dump(resume, f, ensure_ascii=False, indent=2)
    return resume


if __name__ == "__main__":
    evaluer(sys.argv[1], charger())
