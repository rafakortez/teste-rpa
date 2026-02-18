"""
OscarFailScraper — simula falha de scraper em producao.

Cenario: o site mudou o seletor CSS de .film-title para .movie-title.
O scraper carrega a pagina, clica no ano, aguarda o elemento que nao existe
mais (timeout), injeta um banner de erro visual via JS e tira o screenshot.

Util para demonstrar observabilidade: job falha, screenshot mostra a pagina
com o banner vermelho explicando o erro, imagem disponivel via GET /jobs/{id}/screenshot.
"""
import asyncio
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from src.config import settings
from src.scrapers.oscar_scraper import OscarScraper

# seletor que nao existe mais — simula mudanca de estrutura do site
BROKEN_SELECTOR = ".movie-title-v2"
LOAD_TIMEOUT = 8


class OscarFailScraper(OscarScraper):
    """
    Herda de OscarScraper mas usa um seletor CSS inexistente.
    Simula o cenario real onde o site muda sua estrutura HTML
    e o scraper para de funcionar silenciosamente.
    """

    async def execute(self) -> list[dict]:
        driver = self._create_driver()
        try:
            return await asyncio.to_thread(self._scrape_fail, driver)
        except Exception as e:
            # injeta banner de erro visual antes de tirar o screenshot
            try:
                self._inject_error_banner(driver, str(e))
                e.screenshot_bytes = driver.get_screenshot_as_png()
            except Exception:
                pass
            raise e
        finally:
            driver.quit()

    def _inject_error_banner(self, driver: webdriver.Chrome, error_msg: str) -> None:
        """Injeta um banner vermelho na pagina para tornar o erro visivel no screenshot."""
        safe_msg = error_msg.replace("'", "\\'").replace("\n", " ")[:200]
        driver.execute_script(f"""
            var existing = document.getElementById('scraper-error-banner');
            if (existing) existing.remove();

            var banner = document.createElement('div');
            banner.id = 'scraper-error-banner';
            banner.style.cssText = [
                'position: fixed',
                'top: 0',
                'left: 0',
                'width: 100%',
                'background: #c0392b',
                'color: white',
                'font-family: monospace',
                'font-size: 14px',
                'padding: 12px 16px',
                'z-index: 99999',
                'box-shadow: 0 2px 8px rgba(0,0,0,0.5)',
                'border-bottom: 3px solid #922b21'
            ].join(';');

            banner.innerHTML = [
                '<strong>⚠️ SCRAPER ERROR — CSS structure changed</strong><br>',
                '<span style="opacity:0.9">Expected selector:',
                ' <code style="background:#922b21;padding:2px 6px;border-radius:3px">',
                '{BROKEN_SELECTOR}</code>',
                ' — not found after {LOAD_TIMEOUT}s</span><br>',
                '<span style="opacity:0.75;font-size:12px">{safe_msg}</span>'
            ].join('');

            document.body.prepend(banner);
        """)
        time.sleep(0.5)  # garante que o banner renderizou antes do screenshot

    def _scrape_fail(self, driver: webdriver.Chrome) -> list[dict]:
        """Carrega a pagina, clica no primeiro ano e aguarda seletor inexistente."""
        driver.get(settings.oscar_base_url)
        time.sleep(2)  # deixa a pagina carregar completamente

        # clica no primeiro ano para ter contexto visual no screenshot
        try:
            link = driver.find_element(By.ID, "2010")
            link.click()
            time.sleep(1)
        except Exception:
            pass  # se nao achar o link, continua — o erro real vem no wait abaixo

        # aguarda seletor que nao existe — vai dar TimeoutException
        try:
            WebDriverWait(driver, LOAD_TIMEOUT).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, BROKEN_SELECTOR))
            )
        except TimeoutException:
            raise TimeoutException(
                f"Selector '{BROKEN_SELECTOR}' not found after {LOAD_TIMEOUT}s. "
                f"The site may have changed its HTML structure. "
                f"Previously expected '.film-title', got nothing matching '{BROKEN_SELECTOR}'."
            )

        return []
