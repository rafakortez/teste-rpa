import asyncio

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from src.config import settings
from src.scrapers.base_scraper import BaseScraper

YEAR_RANGE = range(2010, 2016)
LOAD_TIMEOUT = 10


class OscarScraper(BaseScraper):

    async def execute(self) -> list[dict]:
        driver = self._create_driver()
        try:
            # to_thread roda selenium em thread separada p nao travar o async
            return await asyncio.to_thread(self._scrape_all_years, driver)
        finally:
            driver.quit()

    def _create_driver(self) -> webdriver.Chrome:
        options = Options()
        options.add_argument("--headless")  # sem janela visivel
        options.add_argument("--no-sandbox")  # obrigatorio dentro de Docker
        options.add_argument("--disable-dev-shm-usage")  # evita crash por memoria em container
        options.add_argument("--disable-gpu")

        if settings.chrome_binary_path:
            options.binary_location = settings.chrome_binary_path

        service_kwargs = {}
        if settings.chromedriver_path:
            service_kwargs["executable_path"] = settings.chromedriver_path

        service = Service(**service_kwargs)
        return webdriver.Chrome(service=service, options=options)

    def _scrape_all_years(self, driver: webdriver.Chrome) -> list[dict]:
        driver.get(settings.oscar_base_url)
        records = []
        for year in YEAR_RANGE:
            year_data = self._scrape_year(driver, year)
            records.extend(year_data)
        return records

    def _scrape_year(self, driver: webdriver.Chrome, year: int) -> list[dict]:
        link = driver.find_element(By.ID, str(year))
        link.click()

        # espera ate o AJAX carregar os filmes (max 10s)
        WebDriverWait(driver, LOAD_TIMEOUT).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, ".film-title"))
        )

        films = []
        rows = driver.find_elements(By.CSS_SELECTOR, "tr.film")
        for row in rows:
            title = row.find_element(By.CSS_SELECTOR, ".film-title").text.strip()
            nominations = int(row.find_element(By.CSS_SELECTOR, ".film-nominations").text.strip())
            awards = int(row.find_element(By.CSS_SELECTOR, ".film-awards").text.strip())
            best = self._is_best_picture(row)
            films.append({
                "title": title,
                "year": year,
                "nominations": nominations,
                "awards": awards,
                "best_picture": best,
            })
        return films

    def _is_best_picture(self, row) -> bool:
        try:
            icon = row.find_element(By.CSS_SELECTOR, ".film-best-picture .glyphicon")
            return icon is not None
        except Exception:
            return False
