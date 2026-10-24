# Interface entre les blocs

Document à valider ensemble avant de coder. Les valeurs ci-dessous sont des propositions de départ, à modifier si le groupe le décide (et à annoncer à tous).

## 1. Score
- Entier de 300 à 850.
- Conversion proposée : `score = 300 + (1 - proba_défaut) * 550`, arrondi à l'entier.

## 2. Modèle IA → API (`ml/`)
- Fichier : `ml/models/model.joblib`
- Fonction : `predict_score(features: dict) -> {"score": int, "explication": [{"variable": str, "impact": float}]}`
- Variables d'entrée : à définir par le responsable IA (régularité des dépôts, montant moyen, fréquence, ancienneté, historique de remboursement, retards).

## 3. API → DApp (`api/`)
Réponse JSON :
```json
{
  "score": 720,
  "explication": [{"variable": "regularite_depots", "impact": 0.12}],
  "nonce": 1,
  "deadline": 1767225600,
  "signature": "0x..."
}
```

## 4. Données signées (EIP-712)
Champs : `borrower` (address), `score` (uint256), `nonce` (uint256), `deadline` (uint256). Domaine : nom, version, `chainId` (Base Sepolia), `verifyingContract`.
Le nonce et la deadline empêchent le rejeu, le chainId lie la signature au réseau.

## 5. Contrat (`contracts/`)
- Adresse du signataire de confiance stockée dans le contrat.
- Paliers proposés (à valider) :

| Score | Collatéral | Taux |
|---|---|---|
| ≥ 700 | 110 % | 5 % |
| 500 à 699 | 150 % | 8 % |
| < 500 | 200 % | 12 % |

## 6. Limites à documenter dans le rapport
- Données synthétiques : le modèle apprend les règles du générateur.
- L'API signataire est un oracle centralisé : si sa clé fuit, les scores peuvent être falsifiés.
- Le score est lié publiquement à l'adresse de l'emprunteur.
