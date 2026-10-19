# code/tout.py : lance tous les tests + évaluations + variante, désigne le meilleur modèle
# usage : python code/tout.py            (3e modèle choisi automatiquement)
#         python code/tout.py <modele>   (3e modèle imposé)
import glob, json, os, subprocess, sys
from groq import Groq
from classifieur import CONSIGNE_EXEMPLES, classer
from evaluer import charger, evaluer

ICI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(ICI, "..", "resultats")
BASE = ["openai/gpt-oss-20b", "openai/gpt-oss-120b"]
EXCLUS = ("guard", "safeguard", "whisper", "tts", "orpheus", "compound", "playai", "embed")


def nom(etiquette):
    return etiquette.replace("/", "_").replace(" ", "_").replace("+", "plus")


def chemin(etiquette):
    return os.path.join(RES, nom(etiquette) + ".json")


def lire(etiquette):
    with open(chemin(etiquette), encoding="utf-8") as f:
        return json.load(f)


def lancer(script):
    subprocess.run([sys.executable, os.path.join(ICI, script)], check=True)


def troisieme():
    for p in glob.glob(os.path.join(RES, "*.json")):
        with open(p, encoding="utf-8") as f:
            r = json.load(f)
        if r["etiquette"] == r["modele"] and not r["modele"].startswith("openai/"):
            return r["modele"]
    ids = sorted(m.id for m in Groq(api_key=os.environ["GROQ_API_KEY"]).models.list().data)
    for mid in ids:
        if mid.startswith("openai/") or any(x in mid.lower() for x in EXCLUS):
            continue
        try:
            classer("Ma facture est trop élevée", mid)
            return mid
        except Exception as e:
            print(f"  {mid} : inaccessible ({type(e).__name__})")
    return None


print("### 1. Tests unitaires des métriques")
lancer("test_evaluation.py")

lignes = charger()
modeles = list(BASE)
m3 = sys.argv[1] if len(sys.argv) > 1 else troisieme()
if m3:
    modeles.append(m3)
    print(f"\n### 2. Troisième modèle : {m3}")
else:
    print("\n### 2. AUCUN troisième modèle accessible : étape 5 incomplète, à signaler.")

for m in modeles:
    if os.path.exists(chemin(m)):
        print(f"\n[déjà fait, ignoré] {m}")
    else:
        print(f"\n### Évaluation : {m}")
        evaluer(m, lignes)

base = sorted((lire(m) for m in modeles), key=lambda r: r["macro_f1"], reverse=True)
meilleur = base[0]
etiq = f"{meilleur['modele'].split('/')[-1]} + 4 exemples"
if os.path.exists(chemin(etiq)):
    print(f"\n[déjà fait, ignoré] {etiq}")
else:
    print(f"\n### Variante few-shot sur le meilleur modèle : {meilleur['modele']}")
    evaluer(meilleur["modele"], lignes, consigne=CONSIGNE_EXEMPLES, etiquette=etiq)

print("\n### Comparaison")
lancer("comparer.py")

var = lire(etiq)
print("\n### VERDICT")
print(f"Meilleur modèle (macro-F1) : {meilleur['modele']}  ({meilleur['macro_f1']:.3f}, {meilleur['n_corrects']}/72, {meilleur['duree_s']} s)")
if len(base) > 1:
    second = base[1]
    ecart = meilleur["n_corrects"] - second["n_corrects"]
    print(f"Écart avec le second ({second['modele']}) : {ecart} ticket(s)")
    if ecart >= 5:
        print("=> Différence mesurable (>= 5 tickets).")
    else:
        print("=> PAS de différence mesurable (< 5 tickets) : départage sur la latence.")
        print("   Durées : " + ", ".join(f"{r['modele']} {r['duree_s']} s" for r in base))
gain = var["n_corrects"] - meilleur["n_corrects"]
print(f"Variante few-shot : {var['macro_f1']:.3f} macro-F1, {gain:+d} ticket(s) vs sans exemples")
