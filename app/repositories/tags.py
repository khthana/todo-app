from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import Tag


class TagRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, name: str) -> Tag:
        normalized = name.strip().lower()
        tag = self.db.query(Tag).filter(func.lower(Tag.name) == normalized).first()
        if tag is None:
            tag = Tag(name=normalized)
            self.db.add(tag)
            self.db.commit()
            self.db.refresh(tag)
        return tag

    def list_all(self) -> list[Tag]:
        return self.db.query(Tag).all()
