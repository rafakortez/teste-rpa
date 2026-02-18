from pydantic import BaseModel


class HockeyTeamResponse(BaseModel):
    # permite ler direto do model SQLAlchemy sem converter pra dict
    model_config = {"from_attributes": True}

    id: str
    job_id: str
    team_name: str
    year: int
    wins: int
    losses: int
    ot_losses: int | None = None
    win_pct: float | None = None
    goals_for: int | None = None
    goals_against: int | None = None
    goal_diff: int | None = None
