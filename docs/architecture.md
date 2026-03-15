# Architecture APS Lab Monitor

## Circulation d'une requête

1. Le client Next.js envoie une requête HTTP vers l'API FastAPI.
2. Le router FastAPI valide l'entrée avec les schémas Pydantic et applique les dépendances, notamment l'authentification JWT.
3. Le service métier orchestre le cas d'usage: lecture ou écriture, règles métier, calcul d'alertes, mise à jour du statut machine.
4. Le repository exécute les requêtes SQLAlchemy synchrones.
5. SQLAlchemy traduit les opérations en SQL pour PostgreSQL.
6. Les données reviennent vers le service, puis sont sérialisées par les schémas de lecture avant la réponse HTTP.

## Rôle des couches

### Routers

Les routers exposent les endpoints HTTP. Ils restent fins: ils reçoivent la requête, injectent les dépendances, appellent le service et retournent une réponse typée.

### Schemas

Les schémas Pydantic servent à deux choses:

- valider les payloads d'entrée
- contrôler la forme des réponses

Ils évitent de renvoyer directement les modèles SQLAlchemy au client.

### Services

Les services portent la logique métier. Exemple: `MeasurementService` enregistre une mesure, évalue les seuils, crée ou désactive les alertes puis met à jour le statut de la machine.

### Repositories

Les repositories centralisent l'accès à la base. Cela rend le code plus lisible, réduit la duplication des requêtes et clarifie la frontière entre métier et persistance.

### Models

Les models SQLAlchemy décrivent la structure relationnelle: tables, colonnes, contraintes, relations, index et enums.

### Migrations

Alembic versionne l'évolution du schéma. La migration initiale crée les tables `users`, `sites`, `machines`, `measurements` et `alerts` avec leurs contraintes.

### Auth JWT

Le login vérifie l'email et le mot de passe hashé, puis renvoie un JWT signé. Les routes protégées lisent ce token via l'entête `Authorization: Bearer ...` et reconstruisent l'utilisateur courant.
