# Guide de lecture du backend Python

Si tu viens de PHP, le plus simple est de lire le backend dans cet ordre :

## 1. La configuration

Commence par [backend/app/core/config.py](/home/nico/dev/aps-lab-monitor/backend/app/core/config.py).

Tu y verras :

- comment Python charge les variables d'environnement
- comment `pydantic-settings` donne des types aux variables
- comment une seule instance de configuration est partagée dans l'application

## 2. Le point d'entrée

Lis ensuite [backend/app/main.py](/home/nico/dev/aps-lab-monitor/backend/app/main.py).

Tu y verras :

- la création de l'application FastAPI
- le CORS
- les handlers d'erreurs
- le startup
- l'inclusion des routes versionnées

## 3. La session base de données

Lis [backend/app/db/session.py](/home/nico/dev/aps-lab-monitor/backend/app/db/session.py).

C'est l'équivalent du point central où l'application sait ouvrir une connexion logique vers PostgreSQL. En SQLAlchemy, on manipule surtout une `Session`.

## 4. Les modèles ORM

Lis ensuite les fichiers de [backend/app/models](/home/nico/dev/aps-lab-monitor/backend/app/models).

Chaque classe décrit :

- une table SQL
- ses colonnes
- ses relations
- ses enums métier

## 5. Les schémas Pydantic

Passe ensuite aux fichiers de [backend/app/schemas](/home/nico/dev/aps-lab-monitor/backend/app/schemas).

Important :

- les `models` décrivent la base
- les `schemas` décrivent les entrées/sorties API

Cette séparation est très importante en Python moderne.

## 6. Les repositories

Lis [backend/app/repositories](/home/nico/dev/aps-lab-monitor/backend/app/repositories).

Un repository centralise les requêtes SQLAlchemy pour une entité ou un groupe de cas simples.

## 7. Les services

Lis ensuite [backend/app/services](/home/nico/dev/aps-lab-monitor/backend/app/services).

C'est là que vit la logique métier :

- authentification
- création machine
- calcul d'alerte
- seed
- agrégation dashboard

Le fichier le plus intéressant à lire est :

- [backend/app/services/measurement_service.py](/home/nico/dev/aps-lab-monitor/backend/app/services/measurement_service.py)

car il montre un vrai flux métier complet.

## 8. Les routers FastAPI

Lis enfin [backend/app/api/v1/endpoints](/home/nico/dev/aps-lab-monitor/backend/app/api/v1/endpoints).

Tu verras que les routes restent fines :

- elles valident les entrées
- appellent les services
- sérialisent les réponses

## 9. Les tests

Termine par [backend/tests/test_api.py](/home/nico/dev/aps-lab-monitor/backend/tests/test_api.py).

Les tests montrent l'application depuis l'extérieur :

- login
- route protégée
- création machine
- création mesure
- création d'alerte
- résumé dashboard

## Parallèle rapide avec PHP

- `main.py` : bootstrap applicatif
- `api/endpoints/*.py` : proche de controllers
- `services/*.py` : proche de services métier
- `repositories/*.py` : proche de repositories / queries dédiées
- `models/*.py` : ORM
- `schemas/*.py` : DTO / Request / Response objects
- `deps.py` : injection de dépendances réutilisable

## Fichiers prioritaires à lire

Si tu veux aller vite, lis dans cet ordre :

1. [backend/app/core/config.py](/home/nico/dev/aps-lab-monitor/backend/app/core/config.py)
2. [backend/app/db/session.py](/home/nico/dev/aps-lab-monitor/backend/app/db/session.py)
3. [backend/app/api/deps.py](/home/nico/dev/aps-lab-monitor/backend/app/api/deps.py)
4. [backend/app/services/auth_service.py](/home/nico/dev/aps-lab-monitor/backend/app/services/auth_service.py)
5. [backend/app/services/measurement_service.py](/home/nico/dev/aps-lab-monitor/backend/app/services/measurement_service.py)
6. [backend/app/api/v1/endpoints/measurements.py](/home/nico/dev/aps-lab-monitor/backend/app/api/v1/endpoints/measurements.py)
7. [backend/tests/test_api.py](/home/nico/dev/aps-lab-monitor/backend/tests/test_api.py)
