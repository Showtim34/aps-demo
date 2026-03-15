"""Classe de base déclarative partagée par tous les modèles SQLAlchemy."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Classe parente de tous les modèles ORM.

    Chaque modèle SQLAlchemy hérite de cette classe afin que SQLAlchemy puisse
    enregistrer toutes les tables mappées dans un même objet `metadata`.
    """

    pass
