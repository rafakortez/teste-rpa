from pydantic import BaseModel


class OscarFilmResponse(BaseModel):
    # permite ler direto do model SQLAlchemy sem converter pra dict
    model_config = {"from_attributes": True}

    id: str
    job_id: str
    title: str
    year: int
    nominations: int
    awards: int
    best_picture: bool
