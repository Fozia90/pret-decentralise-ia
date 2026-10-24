# Règles de travail

1. Ne jamais pousser directement sur `main`.
2. Chacun travaille sur sa branche, nommée `<bloc>/<sujet>` : `ml/modele-xgboost`, `api/signature`, `contracts/pret`, `dapp/accueil`.
3. Pour intégrer son travail : ouvrir une pull request vers `main`, demander une relecture à un autre membre.
4. Chacun ne modifie que son dossier. Un changement dans `docs/interface.md` doit être annoncé au groupe avant la pull request.
5. Messages de commit courts et clairs, par exemple `api: ajoute la signature EIP-712`.
6. **Aucun secret dans le dépôt** : clés privées, fichiers `.env`, phrases de récupération. Utiliser `.env.example` comme modèle. Si une clé est poussée par erreur, la considérer comme compromise et en générer une nouvelle.
