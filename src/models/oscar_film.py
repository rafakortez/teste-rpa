import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base_entity import BaseEntity


class OscarFilm(BaseEntity):
    __tablename__ = "oscar_films"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("crawl_jobs.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    nominations: Mapped[int] = mapped_column(Integer, nullable=False)
    awards: Mapped[int] = mapped_column(Integer, nullable=False)
    best_picture: Mapped[bool] = mapped_column(Boolean, default=False)
