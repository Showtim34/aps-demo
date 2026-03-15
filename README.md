# Factory Monitor

Factory Monitor est un mini projet full stack de supervision industrielle. Il a été conçu comme un support d'apprentissage sérieux pour comprendre une architecture backend Python moderne avec FastAPI, SQLAlchemy, Pydantic, Alembic, JWT et un front Next.js lisible.

## Objectif du projet

L'application permet de:

- gérer des sites industriels
- gérer des machines rattachées à un site
- enregistrer des mesures capteurs
- calculer automatiquement des alertes selon des seuils
- afficher un dashboard de supervision
- sécuriser les routes métier avec une authentification JWT admin

## Stack

### Backend

- Python 3.12
- FastAPI
- SQLAlchemy 2.x en mode synchrone
- Pydantic v2
- pydantic-settings
- PostgreSQL avec `psycopg`
- Alembic
- JWT avec `PyJWT`
- Hash de mot de passe avec `pwdlib`
- MQTT avec `paho-mqtt`
- pytest + httpx/TestClient
- ruff

### Frontend

- Next.js App Router
- React
- TypeScript
- fetch API native
- MQTT over WebSocket avec `mqtt.js`
- Recharts pour le graphique
- une seconde interface Next.js orientée opérations sur le port `4000`

### Infra

- Docker Compose
- PostgreSQL
- Eclipse Mosquitto comme broker MQTT
- un conteneur API
- un conteneur front

## Pourquoi ces choix

### Pourquoi FastAPI

FastAPI offre une API claire, typée, rapide à lire et pratique pour exposer des endpoints métier. Sa gestion des dépendances et l'intégration avec Pydantic sont très pédagogiques.

### Pourquoi SQLAlchemy

SQLAlchemy est une base incontournable en Python pour modéliser des relations SQL sérieuses. Ici il est utilisé en mode synchrone volontairement pour rester simple à lire quand on débute en Python backend.

### Pourquoi Alembic

Alembic versionne le schéma de base de données. Le projet montre qu'un schéma SQL ne doit pas vivre seulement dans les modèles Python: il doit aussi être piloté par des migrations.

### Pourquoi Pydantic

Pydantic sépare clairement validation d'entrée, sérialisation de sortie et modèles ORM. Cela rend les contrats d'API explicites.

### Pourquoi repository + service

Cette séparation évite de mettre les requêtes SQL dans les routes et la logique métier dans les controllers. Les routers restent fins, les services portent le métier, les repositories portent la persistance.

### Pourquoi Docker Compose

Docker Compose simplifie le lancement coordonné de PostgreSQL, de l'API et du front. C'est utile pour obtenir un environnement local stable, proche d'un contexte d'équipe.

### Pourquoi séparer front / API / DB

Cette séparation reflète une architecture web classique et rend chaque responsabilité plus simple à comprendre, tester et faire évoluer.

## Arborescence

```text
.
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── Dockerfile
│   └── package.json
├── frontend-ops/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── Dockerfile
│   └── package.json
├── docs/
│   ├── architecture.md
│   ├── python-backend-course.md
│   └── python-backend-reading-guide.md
├── .env.example
├── docker-compose.yml
└── README.md
```

## Backend: rôle des grandes couches

### `app/core`

- configuration centralisée via `pydantic-settings`
- sécurité JWT et hash de mot de passe
- exceptions métier
- logging applicatif

### `app/db`

- définition de la base SQLAlchemy
- moteur et session synchrones

### `app/models`

- mapping ORM relationnel
- enums métier
- contraintes SQL, index et relations

### `app/schemas`

- payloads d'entrée et réponses API
- séparation claire entre écriture et lecture

### `app/repositories`

- requêtes SQLAlchemy centralisées
- lecture/écriture persistante isolée du métier

### `app/services`

- orchestration métier
- auth, seed, dashboard, mesures, alertes, machines

### `app/api`

- routers FastAPI versionnés
- dépendances d'auth et de base de données

## Frontend: rôle des grandes parties

### `app/`

Les pages Next.js. `login` gère l'authentification, `dashboard` affiche la supervision, `machines/[machineId]` affiche le détail d'une machine.

### `components/dashboard/`

Les composants métier du tableau de bord: cartes de synthèse, tableau de machines, liste d'alertes, formulaire de mesure, graphique, formulaire de login.

### `components/ui/`

Petits composants visuels réutilisables, ici le badge de statut.

### `lib/`

Client API, gestion simple du token et types partagés côté front.

## Frontend Ops: interface d'action

Le dossier `frontend-ops/` contient une seconde application Next.js dédiée aux actions manuelles:

- login admin
- lancement du seed de démonstration
- création de sites
- création de machines
- publication MQTT d'une mesure `warning`
- publication MQTT d'une mesure `critical`
- publication MQTT d'une mesure normale pour fermer une alerte

## Lancement rapide avec Docker Compose

1. Copier l'environnement:

```bash
cp .env.example .env
```

2. Construire et démarrer:

```bash
docker compose up --build
```

3. Ouvrir:

- front: http://localhost:3000
- ops: http://localhost:4000
- API docs: http://localhost:8000/docs
- healthcheck: http://localhost:8000/health
- broker MQTT TCP: `localhost:1883`
- broker MQTT WebSocket: `ws://localhost:9001`

## Migrations

La migration initiale est fournie dans `backend/alembic/versions/20260312_0001_initial_schema.py`.

### Lancer les migrations dans le conteneur API

```bash
docker compose exec api alembic upgrade head
```

### Créer une nouvelle migration plus tard

```bash
docker compose exec api alembic revision --autogenerate -m "add new feature"
```

## Seed de démonstration

Un utilisateur admin de démonstration est garanti au démarrage pour permettre le login. Le endpoint de seed complète ensuite les sites, machines, mesures et alertes de démonstration.

### Lancer le seed via l'API

1. Se connecter avec le compte admin
2. Appeler `POST /api/v1/demo/seed`

Exemple avec `curl`:

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' | jq -r .access_token)

curl -X POST http://localhost:8000/api/v1/demo/seed \
  -H "Authorization: Bearer $TOKEN"
```

Le seed est idempotent sur les entités principales: il ne recrée pas l'admin, les sites ou les machines si elles existent déjà, et il évite de recréer des mesures si une machine en possède déjà.

## Connexion

- email: `admin@example.com`
- password: `admin123`

## Commandes de test

### Depuis le backend local

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

### Depuis Docker

```bash
docker compose exec api pytest
```

## Routes principales

### Publiques

- `GET /health`
- `POST /api/v1/auth/login`

### Protégées

- `GET /api/v1/users/me`
- `GET /api/v1/sites`
- `POST /api/v1/sites`
- `GET /api/v1/sites/{site_id}`
- `GET /api/v1/machines`
- `POST /api/v1/machines`
- `GET /api/v1/machines/{machine_id}`
- `PATCH /api/v1/machines/{machine_id}`
- `GET /api/v1/machines/{machine_id}/measurements`
- `POST /api/v1/measurements`
- `GET /api/v1/alerts`
- `POST /api/v1/demo/seed`
- `GET /api/v1/dashboard/summary`

## Règles métier sur les mesures

À chaque création de mesure:

- si `temperature > 95` ou `vibration > 8` ou `power > 98`, une alerte `critical` est créée ou maintenue
- sinon si `temperature > 80` ou `vibration > 6` ou `power > 90`, une alerte `warning` est créée ou maintenue
- sinon les alertes actives de la machine sont désactivées
- le statut machine devient `alert` si un seuil est dépassé
- le statut machine devient `running` si la mesure est normale
- le statut par défaut d'une machine créée est `idle`

## Flux complet d'une mesure

1. Une mesure arrive soit par HTTP, soit par MQTT sur `monitor/telemetry/measurements`.
2. Le backend Python valide le payload avec `MeasurementCreate`.
3. `MeasurementService` vérifie que la machine existe.
4. `MeasurementRepository` écrit la mesure en base.
5. `MeasurementService` évalue les seuils.
6. Si nécessaire, `AlertRepository` crée ou met à jour une alerte active.
7. Si aucun seuil n'est dépassé, les alertes actives sont désactivées.
8. Le statut de la machine est mis à jour.
9. Le backend publie un événement MQTT de dashboard.
10. Le dashboard Next.js sur `:3000` reçoit cet événement et se rafraîchit en temps réel.

## Architecture MQTT

Le projet montre maintenant deux usages complémentaires de MQTT:

- Python backend avec `paho-mqtt`
  - l'API s'abonne au topic `monitor/telemetry/measurements`
  - elle consomme les messages et applique la logique métier normale
  - elle publie ensuite des événements sur `monitor/events/dashboard`

- Next.js avec `mqtt.js`
  - le dashboard principal sur `:3000` s'abonne à `monitor/events/dashboard`
  - la console ops sur `:4000` publie des mesures sur `monitor/telemetry/measurements`

Ainsi, tu vois à la fois:

- MQTT côté Python
- MQTT côté Next.js
- la différence entre un producteur de messages et un consommateur
- un vrai cycle temps réel de bout en bout

## Développement local sans Docker

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Pensez à définir `NEXT_PUBLIC_API_URL=http://localhost:8000`.

## Ce que montre ce projet

- settings via variables d'environnement
- session DB SQLAlchemy sync
- modèles relationnels explicites
- schémas Pydantic d'entrée et sortie
- séparation router / service / repository
- sécurité JWT lisible
- seed de démonstration
- migrations Alembic
- tests API lisibles

## Lecture conseillée si tu viens de PHP

J'ai ajouté un guide de lecture backend dans [docs/python-backend-reading-guide.md](/home/nico/dev/aps-lab-monitor/docs/python-backend-reading-guide.md) pour t'aider à parcourir le code Python dans le bon ordre.

Si tu veux une version plus pédagogique, plus longue et pensée comme un mini cours, lis [docs/python-backend-course.md](/home/nico/dev/aps-lab-monitor/docs/python-backend-course.md).

## Pistes d'amélioration futures

- ajouter une pagination sur les listes
- enrichir les alertes avec accusé de réception et historique
- gérer plusieurs rôles utilisateurs
- ajouter des jobs de génération continue de mesures
- introduire des tests front automatisés
- ajouter observabilité et métriques applicatives
