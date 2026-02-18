from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "APP_"}

    database_url: str = "postgresql+asyncpg://scraper:scraper@localhost:5432/scraper_db"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    selenium_remote_url: str | None = None
    chrome_binary_path: str | None = None
    chromedriver_path: str | None = None

    hockey_base_url: str = "https://www.scrapethissite.com/pages/forms/"
    oscar_base_url: str = "https://www.scrapethissite.com/pages/ajax-javascript/"


settings = Settings()
