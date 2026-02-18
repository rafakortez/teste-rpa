import uuid

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base_entity import BaseEntity


class HockeyTeam(BaseEntity):
    __tablename__ = "hockey_teams"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("crawl_jobs.id"), nullable=False
    )
    team_name: Mapped[str] = mapped_column(String(255), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    wins: Mapped[int] = mapped_column(Integer, nullable=False)
    losses: Mapped[int] = mapped_column(Integer, nullable=False)
    ot_losses: Mapped[int | None] = mapped_column(Integer, nullable=True)
    win_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    goals_for: Mapped[int | None] = mapped_column(Integer, nullable=True)
    goals_against: Mapped[int | None] = mapped_column(Integer, nullable=True)
    goal_diff: Mapped[int | None] = mapped_column(Integer, nullable=True)
