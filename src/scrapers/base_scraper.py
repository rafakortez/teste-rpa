from abc import ABC, abstractmethod


# contrato: todo scraper novo implementa execute() sem mudar os existentes
class BaseScraper(ABC):

    @abstractmethod
    async def execute(self) -> list[dict]:
        """
        Run the scraping logic and return a list of raw dictionaries.
        Each dictionary represents one scraped record.
        """
        ...
