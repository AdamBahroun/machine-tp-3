from evaluation import accuracy, scores_par_classe, f1_macro, matrice_confusion

vrais   = ["compte", "technique", "compte", "commercial"]
predits = ["compte", "technique", "commercial", "commercial"]
print("Accuracy :", accuracy(vrais, predits))
print("Scores :", scores_par_classe(vrais, predits))
print("Macro-F1 :", f1_macro(scores_par_classe(vrais, predits)))
print("Matrice :", matrice_confusion(vrais, predits))

# Points de contrôle de l'énoncé
assert accuracy(vrais, vrais) == 1.0
assert abs(f1_macro(scores_par_classe(vrais, vrais, ["compte", "technique", "commercial"])) - 1.0) < 1e-9
scores_par_classe(vrais, ["compte"] * 4)   # une seule classe prédite : ne doit pas planter
print("OK : tous les contrôles passent")
