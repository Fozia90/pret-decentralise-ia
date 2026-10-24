"""
Entraînement du modèle de score de crédit.

Usage (depuis la racine du dépôt) :
    python ml/train_model.py
    python ml/train_model.py --seuil 0.25

Étapes : régression logistique (référence) puis XGBoost, comparés sur le même
jeu de test. Le modèle XGBoost est sauvegardé dans ml/models/model.joblib, car
c'est lui que l'API utilisera avec SHAP.
"""
import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (brier_score_loss, confusion_matrix,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

ICI = Path(__file__).resolve().parent
CSV = ICI / "data" / "clients_synthetiques.csv"
SORTIE = ICI / "models"

# Ordre des variables : à respecter partout (API, tests). Voir docs/interface.md
FEATURES = [
    "anciennete_mois",
    "depot_moyen_usd",
    "regularite_depots",
    "frequence_transactions",
    "ratio_depenses_revenus",
    "nb_prets_precedents",
    "nb_retards_12m",
]
CIBLE = "defaut"


def evaluer(nom, modele, X_test, y_test, seuil):
    proba = modele.predict_proba(X_test)[:, 1]
    pred = (proba >= seuil).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
    res = {
        "modele": nom,
        "auc": round(float(roc_auc_score(y_test, proba)), 4),
        "brier": round(float(brier_score_loss(y_test, proba)), 4),
        "precision": round(float(precision_score(y_test, pred, zero_division=0)), 4),
        "rappel": round(float(recall_score(y_test, pred)), 4),
        "matrice": {"vrais_negatifs": int(tn), "faux_positifs": int(fp),
                    "faux_negatifs": int(fn), "vrais_positifs": int(tp)},
    }
    print(f"\n=== {nom} (seuil de décision = {seuil}) ===")
    print(f"AUC       : {res['auc']}")
    print(f"Brier     : {res['brier']}  (plus petit = probabilités mieux calibrées)")
    print(f"Précision : {res['precision']}   Rappel : {res['rappel']}")
    print(f"Matrice   : VN={tn}  FP={fp}  FN={fn}  VP={tp}")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seuil", type=float, default=0.3,
                    help="seuil de probabilité de défaut pour la matrice de confusion")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    df = pd.read_csv(CSV)
    X, y = df[FEATURES], df[CIBLE]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=args.seed)
    print(f"Entraînement : {len(X_train)} clients, test : {len(X_test)} clients, "
          f"taux de défaut : {y.mean():.1%}")

    ref = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    ref.fit(X_train, y_train)
    res_ref = evaluer("Régression logistique (référence)", ref, X_test, y_test, args.seuil)

    xgb = XGBClassifier(
        n_estimators=300, max_depth=3, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8,
        eval_metric="logloss", random_state=args.seed)
    xgb.fit(X_train, y_train)
    res_xgb = evaluer("XGBoost", xgb, X_test, y_test, args.seuil)

    SORTIE.mkdir(exist_ok=True)
    joblib.dump({"model": xgb, "features": FEATURES}, SORTIE / "model.joblib")
    with open(SORTIE / "metrics.json", "w", encoding="utf-8") as f:
        json.dump({"seuil": args.seuil, "resultats": [res_ref, res_xgb]}, f,
                  indent=2, ensure_ascii=False)
    print(f"\nModèle sauvegardé : {SORTIE / 'model.joblib'}")
    print(f"Métriques         : {SORTIE / 'metrics.json'}")


if __name__ == "__main__":
    main()