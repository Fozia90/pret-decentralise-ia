"""
Génération de données synthétiques de type mobile money pour le scoring de crédit.

Usage (depuis la racine du dépôt) :
    python ml/generate_data.py --n 8000 --seed 42 --out ml/data/clients_synthetiques.csv

Principe : on tire des variables réalistes, puis on définit une probabilité de
défaut de paiement par une formule logistique + du bruit. Le modèle d'IA devra
ensuite retrouver ces relations à partir des données seules.

ATTENTION (à écrire dans le rapport) : les règles ci-dessous viennent de nous,
pas du monde réel. Un bon score du modèle prouve qu'il a appris notre générateur,
pas qu'il prédit de vrais défauts.
"""
import argparse
import numpy as np
import pandas as pd

# Poids du générateur : signe négatif = réduit le risque de défaut.
# Hypothèses du groupe, à ajuster et à documenter.
POIDS = {
    "regularite_depots": -2.0,         # dépôts réguliers -> moins de défaut
    "anciennete_mois": -0.02,          # compte ancien -> moins de défaut
    "log_depot_moyen": -0.35,          # revenus plus élevés -> moins de défaut
    "ratio_depenses_revenus": 2.0,     # dépenses proches des revenus -> plus de défaut
    "nb_retards_12m": 0.45,            # retards récents -> plus de défaut
    "nb_prets_precedents": -0.10,      # expérience de crédit -> légèrement moins de défaut
    "log_frequence": -0.25,            # activité plus fréquente -> légèrement moins de défaut
}
BRUIT_STD = 0.8          # part de hasard non expliquée par les variables
TAUX_DEFAUT_CIBLE = 0.15 # environ 15 % de défauts


def generer_variables(n, rng):
    anciennete = rng.integers(1, 85, n)                              # mois
    depot_moyen = np.round(rng.lognormal(mean=4.2, sigma=0.7, size=n), 2)  # USD / mois
    regularite = np.clip(rng.beta(4, 2, n), 0, 1)                    # 0 à 1
    frequence = rng.poisson(18, n) + 1                               # transactions / mois
    ratio = np.clip(rng.normal(0.8, 0.18, n), 0.3, 1.4)              # dépenses / revenus
    nb_prets = rng.poisson(1.5, n)
    # Les retards dépendent un peu de la régularité (réalisme), pas seulement du hasard.
    lam_retards = np.clip(1.2 * (1 - regularite), 0.02, None)
    nb_retards = rng.poisson(lam_retards)
    nb_retards = np.minimum(nb_retards, 12)
    return pd.DataFrame({
        "anciennete_mois": anciennete,
        "depot_moyen_usd": depot_moyen,
        "regularite_depots": np.round(regularite, 3),
        "frequence_transactions": frequence,
        "ratio_depenses_revenus": np.round(ratio, 3),
        "nb_prets_precedents": nb_prets,
        "nb_retards_12m": nb_retards,
    })


def calculer_logit(df, rng):
    z = (
        POIDS["regularite_depots"] * df["regularite_depots"]
        + POIDS["anciennete_mois"] * df["anciennete_mois"]
        + POIDS["log_depot_moyen"] * np.log(df["depot_moyen_usd"])
        + POIDS["ratio_depenses_revenus"] * df["ratio_depenses_revenus"]
        + POIDS["nb_retards_12m"] * df["nb_retards_12m"]
        + POIDS["nb_prets_precedents"] * df["nb_prets_precedents"]
        + POIDS["log_frequence"] * np.log(df["frequence_transactions"])
    )
    return z + rng.normal(0, BRUIT_STD, len(df))


def calibrer_intercept(z, cible):
    """Cherche l'intercept qui donne le taux de défaut visé (dichotomie)."""
    bas, haut = -30.0, 30.0
    for _ in range(60):
        milieu = (bas + haut) / 2
        taux = (1 / (1 + np.exp(-(z + milieu)))).mean()
        if taux > cible:
            haut = milieu
        else:
            bas = milieu
    return (bas + haut) / 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="ml/data/clients_synthetiques.csv")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    df = generer_variables(args.n, rng)
    z = calculer_logit(df, rng)
    z = z + calibrer_intercept(z, TAUX_DEFAUT_CIBLE)
    proba = 1 / (1 + np.exp(-z))
    df["defaut"] = (rng.random(args.n) < proba).astype(int)

    df.to_csv(args.out, index=False)
    print(f"{args.n} clients écrits dans {args.out}")
    print(f"Taux de défaut : {df['defaut'].mean():.1%}")
    print(df.describe().round(2).T[["mean", "min", "max"]])


if __name__ == "__main__":
    main()