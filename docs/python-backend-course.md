# Comprendre ce backend Python quand on vient de PHP

Ce document est un mini cours de lecture du projet. L'objectif n'est pas de t'apprendre tout Python, mais de te donner les repères concrets pour comprendre une architecture FastAPI moderne sans te perdre.

## 1. Changer de repère mental

Quand on vient de PHP, on cherche souvent des équivalents directs :

- `index.php` ou bootstrap framework -> `backend/app/main.py`
- controllers -> `backend/app/api/v1/endpoints/*.py`
- services métier -> `backend/app/services/*.py`
- repositories -> `backend/app/repositories/*.py`
- entités ORM -> `backend/app/models/*.py`
- DTO / Form Request / Resource -> `backend/app/schemas/*.py`
- config `.env` -> `backend/app/core/config.py`

La grosse différence n'est pas l'architecture. Elle est assez proche d'un projet Symfony ou Laravel bien organisé. La différence est surtout dans la syntaxe Python, le typage moderne et l'écosystème FastAPI/Pydantic/SQLAlchemy.

## 2. Les bases de syntaxe Python utiles pour ce projet

### Indentation

En Python, les blocs ne sont pas délimités par `{}` mais par l'indentation.

Exemple :

```python
def example(value: int) -> str:
    if value > 10:
        return "grand"
    return "petit"
```

### Typage

Le typage est très présent ici.

```python
def get_user(user_id: int) -> User | None:
    ...
```

Cela veut dire :

- `user_id` doit être un `int`
- la fonction retourne soit un `User`, soit `None`

### Classes simples

Les modèles ORM, services et repositories sont des classes Python classiques.

```python
class SiteService:
    def __init__(self, db: Session) -> None:
        self.db = db
```

`self` joue le rôle de `$this`.

## 3. L'ordre conseillé pour lire le projet

Lis dans cet ordre :

1. [backend/app/core/config.py](/home/nico/dev/aps-lab-monitor/backend/app/core/config.py)
2. [backend/app/main.py](/home/nico/dev/aps-lab-monitor/backend/app/main.py)
3. [backend/app/db/session.py](/home/nico/dev/aps-lab-monitor/backend/app/db/session.py)
4. [backend/app/models](/home/nico/dev/aps-lab-monitor/backend/app/models)
5. [backend/app/schemas](/home/nico/dev/aps-lab-monitor/backend/app/schemas)
6. [backend/app/repositories](/home/nico/dev/aps-lab-monitor/backend/app/repositories)
7. [backend/app/services/measurement_service.py](/home/nico/dev/aps-lab-monitor/backend/app/services/measurement_service.py)
8. [backend/app/api/v1/endpoints](/home/nico/dev/aps-lab-monitor/backend/app/api/v1/endpoints)
9. [backend/tests/test_api.py](/home/nico/dev/aps-lab-monitor/backend/tests/test_api.py)

## 4. La configuration

Le fichier [backend/app/core/config.py](/home/nico/dev/aps-lab-monitor/backend/app/core/config.py) centralise toutes les variables d'environnement.

Pourquoi c'est important :

- tu évites de lire `os.environ` partout
- tu gardes des types explicites
- tu définis une seule source de vérité

Exemple :

```python
class Settings(BaseSettings):
    app_name: str = "Factory Monitor"
    app_debug: bool = True
    database_url: str = "postgresql+psycopg://..."
```

Ici, `BaseSettings` va charger automatiquement les valeurs réelles depuis `.env`.

## 5. Le point d'entrée FastAPI

Le fichier [backend/app/main.py](/home/nico/dev/aps-lab-monitor/backend/app/main.py) crée l'application.

Il fait plusieurs choses :

- configure le logging
- démarre l'application
- branche le CORS
- déclare le handler d'erreurs
- expose `/health`
- inclut toutes les routes versionnées

Exemple :

```python
app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    lifespan=lifespan,
)
```

`lifespan` correspond au cycle de vie de l'application : startup + shutdown.

## 6. La base de données avec SQLAlchemy

### `engine`

Dans [backend/app/db/session.py](/home/nico/dev/aps-lab-monitor/backend/app/db/session.py), `engine` représente la connexion globale à la base.

### `Session`

La `Session` SQLAlchemy est l'objet le plus important à comprendre. Elle :

- charge des objets depuis la base
- garde une trace des changements
- écrit en base lors du `commit()`

Tu peux la voir comme une unité de travail.

### Dependency FastAPI

```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

FastAPI injecte cette session dans les routes. Cela remplace beaucoup de boilerplate manuel.

## 7. Les modèles ORM

Les fichiers dans [backend/app/models](/home/nico/dev/aps-lab-monitor/backend/app/models) décrivent les tables.

Exemple :

```python
class Machine(Base):
    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
```

À retenir :

- `Base` est la classe racine commune à tous les modèles
- `mapped_column(...)` décrit une colonne SQL
- `relationship(...)` décrit une relation ORM entre objets

Exemple de relation :

```python
site = relationship("Site", back_populates="machines")
```

Ça ne crée pas une colonne. Ça permet d'accéder à l'objet lié en Python.

## 8. Models vs Schemas

C'est un point central.

### Models

Les `models` représentent la base de données.

### Schemas

Les `schemas` représentent ce qui entre et sort de l'API.

Exemple :

- [backend/app/models/machine.py](/home/nico/dev/aps-lab-monitor/backend/app/models/machine.py) : structure SQL
- [backend/app/schemas/machine.py](/home/nico/dev/aps-lab-monitor/backend/app/schemas/machine.py) : contrat HTTP

Pourquoi séparer :

- éviter d'exposer directement l'ORM
- contrôler les champs acceptés
- contrôler les champs renvoyés

## 9. Les repositories

Les repositories sont là pour isoler les requêtes SQLAlchemy.

Exemple dans [backend/app/repositories/machine_repository.py](/home/nico/dev/aps-lab-monitor/backend/app/repositories/machine_repository.py) :

```python
def get_by_code(self, code: str) -> Machine | None:
    return self.db.scalar(select(Machine).where(Machine.code == code))
```

Le repository répond à une question technique :

"Comment lire ou écrire cette donnée dans PostgreSQL ?"

Il ne devrait pas porter de logique métier complexe.

## 10. Les services

Les services portent les cas d'usage métier.

Exemple :

- `AuthService` : authentifier et générer un token
- `MachineService` : créer ou modifier une machine
- `MeasurementService` : enregistrer une mesure et calculer les alertes
- `DashboardService` : agréger les données utiles au front

Le service répond à une question métier :

"Que doit faire l'application quand il se passe telle action ?"

## 11. Le fichier le plus important : `MeasurementService`

Lis [backend/app/services/measurement_service.py](/home/nico/dev/aps-lab-monitor/backend/app/services/measurement_service.py) avec attention.

C'est le meilleur exemple d'orchestration métier du projet.

Quand une mesure arrive :

1. on vérifie que la machine existe
2. on enregistre la mesure
3. on évalue les seuils
4. on crée ou met à jour une alerte
5. on ferme les alertes si la mesure est normale
6. on met à jour le statut de la machine
7. on commit la transaction
8. on publie un événement MQTT pour rafraîchir les interfaces

Ça montre très bien la séparation :

- repository : accès DB
- service : logique métier
- router ou MQTT consumer : point d'entrée technique

## 12. Les routes FastAPI

Exemple dans [backend/app/api/v1/endpoints/measurements.py](/home/nico/dev/aps-lab-monitor/backend/app/api/v1/endpoints/measurements.py) :

```python
@router.post("", response_model=MeasurementRead, status_code=status.HTTP_201_CREATED)
def create_measurement(
    payload: MeasurementCreate,
    db: DbSession,
    _: Annotated[User, Depends(get_current_user)],
) -> MeasurementRead:
    measurement = MeasurementService(db).create_measurement(payload)
    return MeasurementRead.model_validate(measurement)
```

À lire ligne par ligne :

- `@router.post(...)` : déclaration de la route HTTP
- `payload: MeasurementCreate` : FastAPI parse et valide automatiquement le JSON entrant
- `db: DbSession` : FastAPI injecte une session SQLAlchemy
- `Depends(get_current_user)` : FastAPI impose l'authentification
- `MeasurementService(db).create_measurement(payload)` : la route délègue le métier au service
- `MeasurementRead.model_validate(...)` : conversion vers le schéma de sortie

## 13. L'authentification JWT

Le flux est simple :

1. le client appelle `POST /api/v1/auth/login`
2. `AuthService` vérifie email + mot de passe hashé
3. `create_access_token(...)` crée un JWT signé
4. le client le renvoie ensuite dans `Authorization: Bearer ...`
5. `get_current_user` décode le token et recharge l'utilisateur

Les fichiers importants :

- [backend/app/core/security.py](/home/nico/dev/aps-lab-monitor/backend/app/core/security.py)
- [backend/app/api/deps.py](/home/nico/dev/aps-lab-monitor/backend/app/api/deps.py)
- [backend/app/services/auth_service.py](/home/nico/dev/aps-lab-monitor/backend/app/services/auth_service.py)

## 14. MQTT dans ce projet

Le projet montre maintenant deux flux d'entrée :

### HTTP

Le front ou un outil appelle directement `POST /api/v1/measurements`.

### MQTT

Une application publie une mesure sur :

```text
monitor/telemetry/measurements
```

Le backend Python, via [backend/app/realtime/mqtt.py](/home/nico/dev/aps-lab-monitor/backend/app/realtime/mqtt.py), est abonné à ce topic.

Important : le consommateur MQTT ne réécrit pas la logique métier. Il reconstruit un `MeasurementCreate` et appelle `MeasurementService`. C'est exactement ce qu'on veut dans une architecture propre.

## 15. Pourquoi le dashboard se met à jour en temps réel

Après chaque mesure traitée, le backend publie un événement MQTT sur :

```text
monitor/events/dashboard
```

Le front `:3000` s'abonne à ce topic avec `mqtt.js`. Dès qu'un événement arrive, il recharge ou remplace son état local avec le résumé envoyé par le backend.

Tu vois donc un vrai flux temps réel :

- un producteur publie
- le backend consomme
- le backend applique le métier
- le backend republie un événement
- le dashboard s'abonne et se rafraîchit

## 16. Les tests

Lis [backend/tests/test_api.py](/home/nico/dev/aps-lab-monitor/backend/tests/test_api.py) comme une documentation exécutable.

Les tests te montrent :

- comment on se logue
- comment on appelle une route protégée
- comment on crée une machine
- comment une mesure déclenche une alerte

Pour un débutant, les tests sont souvent le meilleur moyen de comprendre l'usage d'un code.

## 17. Les points Python à retenir dans ce code

- `self` = l'équivalent de `$this`
- `None` = l'équivalent de `null`
- `User | None` = union de types
- `dict[str, Any]` = tableau associatif typé
- les docstrings `"""..."""` servent à documenter classes et fonctions
- `@router.get`, `@router.post` sont des décorateurs
- `Depends(...)` est le système d'injection de dépendances FastAPI

## 18. Stratégie de progression

Je te conseille cette méthode :

1. lire une route
2. regarder son schéma d'entrée
3. regarder le service appelé
4. regarder les repositories utilisés
5. regarder les modèles ORM touchés
6. finir par le test correspondant

Exemple concret :

1. [backend/app/api/v1/endpoints/measurements.py](/home/nico/dev/aps-lab-monitor/backend/app/api/v1/endpoints/measurements.py)
2. [backend/app/schemas/measurement.py](/home/nico/dev/aps-lab-monitor/backend/app/schemas/measurement.py)
3. [backend/app/services/measurement_service.py](/home/nico/dev/aps-lab-monitor/backend/app/services/measurement_service.py)
4. [backend/app/repositories/measurement_repository.py](/home/nico/dev/aps-lab-monitor/backend/app/repositories/measurement_repository.py)
5. [backend/app/models/measurement.py](/home/nico/dev/aps-lab-monitor/backend/app/models/measurement.py)
6. [backend/tests/test_api.py](/home/nico/dev/aps-lab-monitor/backend/tests/test_api.py)

## 19. Ce qu'il ne faut pas retenir de travers

- Python n'est pas "magique" ici : la structure reste très explicite
- FastAPI n'oblige pas à faire de l'async partout
- SQLAlchemy sync reste très bien pour apprendre proprement
- MQTT n'est qu'un mode d'entrée/sortie de messages en plus, pas un remplacement de l'API HTTP

## 20. Lecture finale recommandée

Si tu veux comprendre le projet en profondeur, lis dans cet ordre exact :

1. [docs/python-backend-reading-guide.md](/home/nico/dev/aps-lab-monitor/docs/python-backend-reading-guide.md)
2. [backend/app/core/config.py](/home/nico/dev/aps-lab-monitor/backend/app/core/config.py)
3. [backend/app/main.py](/home/nico/dev/aps-lab-monitor/backend/app/main.py)
4. [backend/app/db/session.py](/home/nico/dev/aps-lab-monitor/backend/app/db/session.py)
5. [backend/app/models/machine.py](/home/nico/dev/aps-lab-monitor/backend/app/models/machine.py)
6. [backend/app/schemas/machine.py](/home/nico/dev/aps-lab-monitor/backend/app/schemas/machine.py)
7. [backend/app/repositories/machine_repository.py](/home/nico/dev/aps-lab-monitor/backend/app/repositories/machine_repository.py)
8. [backend/app/services/machine_service.py](/home/nico/dev/aps-lab-monitor/backend/app/services/machine_service.py)
9. [backend/app/services/measurement_service.py](/home/nico/dev/aps-lab-monitor/backend/app/services/measurement_service.py)
10. [backend/app/realtime/mqtt.py](/home/nico/dev/aps-lab-monitor/backend/app/realtime/mqtt.py)
11. [backend/tests/test_api.py](/home/nico/dev/aps-lab-monitor/backend/tests/test_api.py)
