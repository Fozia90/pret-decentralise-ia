"""
Fonction utilisée par l'API : calcule le score (300 à 850) et l'explication SHAP.

Exemple :
    from ml.predict import predict_score
    predict_score({
        "anciennete_mois": 36, "depot_moyen_usd": 90.0, "regularite_depots": 0.8,
        "frequence_transactions": 20, "ratio_depenses_revenus": 0.7,
        "nb_prets_precedents": 2, "nb_retards_12m": 0,
    })
"""
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
import shap

CHEMIN_MODELE = Path(__file__).resolve().parent / "models" / "model.joblib"
SCORE_MIN, SCORE_MAX = 300, 850


@lru_cache(maxsize=1)
def _charger():
    bundle = joblib.load(CHEMIN_MODELE)
    return bundle["model"], bundle["features"], shap.TreeExplainer(bundle["model"])


def proba_vers_score(proba_defaut: float) -> int:
    """score = 300 + (1 - proba_défaut) * 550, arrondi à l'entier."""
    score = SCORE_MIN + (1.0 - proba_defaut) * (SCORE_MAX - SCORE_MIN)
    return int(round(min(max(score, SCORE_MIN), SCORE_MAX)))


def predict_score(features: dict, top: int = 5) -> dict:
    model, noms, explainer = _charger()
    manquantes = [n for n in noms if n not in features]
    if manquantes:
        raise ValueError(f"Variables manquantes : {manquantes}")

    X = pd.DataFrame([[features[n] for n in noms]], columns=noms)
    proba = float(model.predict_proba(X)[0, 1])

    valeurs = explainer.shap_values(X)
    if isinstance(valeurs, list):      # selon la version de shap
        valeurs = valeurs[1]
    contributions = valeurs[0]

    # Convention : impact positif = cette variable AMÉLIORE le score
    # (SHAP mesure l'effet sur le risque de défaut, on inverse le signe).
    impacts = sorted(
        ({"variable": n, "impact": round(-float(c), 4)} for n, c in zip(noms, contributions)),
        key=lambda d: abs(d["impact"]), reverse=True)[:top]

    return {"score": proba_vers_score(proba), "explication": impacts}