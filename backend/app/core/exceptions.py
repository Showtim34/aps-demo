"""Exceptions applicatives personnalisées.

Au lieu de lever des `HTTPException` partout, les services lèvent des erreurs
orientées métier. `app.main` les traduit ensuite en réponses HTTP à un seul
endroit.
"""

class AppError(Exception):
    """Classe de base pour les erreurs métier/applicatives connues."""

    status_code = 400

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    """Levée lorsqu'une ressource métier demandée n'existe pas."""
    status_code = 404


class UnauthorizedError(AppError):
    """Levée lorsqu'une authentification échoue ou qu'un token est invalide."""
    status_code = 401


class ConflictError(AppError):
    """Levée lorsqu'une opération viole une contrainte métier ou d'unicité."""
    status_code = 409
