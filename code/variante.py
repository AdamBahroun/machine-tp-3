# code/variante.py : même modèle, consigne enrichie (few-shot)
# usage : python variante.py <meilleur_modele_de_l_etape_5>
import sys
from classifieur import CONSIGNE_EXEMPLES
from evaluer import evaluer, charger

modele = sys.argv[1] if len(sys.argv) > 1 else "openai/gpt-oss-120b"
evaluer(modele, charger(), consigne=CONSIGNE_EXEMPLES,
        etiquette=f"{modele.split('/')[-1]} + 4 exemples")
