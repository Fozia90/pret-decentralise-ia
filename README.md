# Prêt décentralisé avec score de crédit calculé par l'IA

Projet du Groupe 21 – Blockchain et intelligence artificielle.

Un modèle d'IA calcule un score de crédit à partir de données (synthétiques) de mobile money. Une API signe ce score (EIP-712). Un contrat intelligent vérifie la signature et ajuste le collatéral et le taux du prêt selon le score. Une DApp permet à l'emprunteur d'utiliser le tout.

## Architecture

DApp React → API FastAPI → Modèle IA (XGBoost + SHAP) → score signé (EIP-712) → DApp → Contrat Solidity (Base Sepolia)

Détails et formats à respecter : `docs/interface.md`.

## Organisation du dépôt

| Dossier | Contenu | Responsable |
|---|---|---|
| `ml/` | Données synthétiques, entraînement, modèle, SHAP | _à remplir_ |
| `api/` | API FastAPI, signature EIP-712 | _à remplir_ |
| `contracts/` | Contrat Solidity, tests Foundry | _à remplir_ |
| `dapp/` | Interface web React | _à remplir_ |
| `docs/` | Interface entre les blocs, rapport | tous |

Le responsable de l'intégration rassemble les parties et écrit les tests de bout en bout.

## Déploiement prévu

- API et modèle : Render ou Hugging Face Spaces
- Contrats : Base Sepolia (testnet)
- DApp : Vercel

## Règles de travail

Voir `CONTRIBUTING.md`.
