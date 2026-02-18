import httpx
from bs4 import BeautifulSoup

from src.config import settings
from src.scrapers.base_scraper import BaseScraper

TOTAL_PAGES = 24


class HockeyScraper(BaseScraper):

    async def execute(self) -> list[dict]:
        records = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for page in range(1, TOTAL_PAGES + 1):
                html = await self._fetch_page(client, page)
                rows = self._parse_page(html)
                records.extend(rows)
        return records

    async def _fetch_page(self, client: httpx.AsyncClient, page: int) -> str:
        url = f"{settings.hockey_base_url}?page_num={page}"
        response = await client.get(url)
        response.raise_for_status()
        return response.text

    def _parse_page(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        teams = []
        for row in soup.select("tr.team"):
            team = {
                "team_name": self._text(row, ".name"),
                "year": self._int(row, ".year"),
                "wins": self._int(row, ".wins"),
                "losses": self._int(row, ".losses"),
                "ot_losses": self._int_or_none(row, ".ot-losses"),
                "win_pct": self._float_or_none(row, ".pct"),
                "goals_for": self._int_or_none(row, ".gf"),
                "goals_against": self._int_or_none(row, ".ga"),
                "goal_diff": self._int_or_none(row, ".diff"),
            }
            teams.append(team)
        return teams

    def _text(self, row, selector: str) -> str:
        element = row.select_one(selector)
        return element.text.strip() if element else ""

    def _int(self, row, selector: str) -> int:
        return int(self._text(row, selector))

    def _int_or_none(self, row, selector: str) -> int | None:
        raw = self._text(row, selector)
        if not raw:
            return None
        return int(raw)

    def _float_or_none(self, row, selector: str) -> float | None:
        raw = self._text(row, selector)
        if not raw:
            return None
        return float(raw)
