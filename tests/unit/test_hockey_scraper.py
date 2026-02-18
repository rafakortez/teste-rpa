from src.scrapers.hockey_scraper import HockeyScraper

# HTML fake que simula uma linha da tabela real do site
FAKE_ROW = """
<tr class="team">
  <td class="name">Boston Bruins</td>
  <td class="year">2020</td>
  <td class="wins">44</td>
  <td class="losses">14</td>
  <td class="ot-losses">12</td>
  <td class="pct">0.714</td>
  <td class="gf">227</td>
  <td class="ga">174</td>
  <td class="diff">53</td>
</tr>
"""

FAKE_PAGE = f"<table>{FAKE_ROW}</table>"


def test_parse_page_extrai_todos_campos():
    scraper = HockeyScraper()
    result = scraper._parse_page(FAKE_PAGE)

    assert len(result) == 1
    team = result[0]
    assert team["team_name"] == "Boston Bruins"
    assert team["year"] == 2020
    assert team["wins"] == 44
    assert team["losses"] == 14
    assert team["ot_losses"] == 12
    assert team["win_pct"] == 0.714
    assert team["goals_for"] == 227
    assert team["goals_against"] == 174
    assert team["goal_diff"] == 53


def test_parse_page_campo_vazio_retorna_none():
    """Testa que campos ausentes viram None em vez de erro."""
    html = """
    <table>
      <tr class="team">
        <td class="name">Empty Team</td>
        <td class="year">2021</td>
        <td class="wins">10</td>
        <td class="losses">5</td>
        <td class="ot-losses"></td>
        <td class="pct"></td>
        <td class="gf"></td>
        <td class="ga"></td>
        <td class="diff"></td>
      </tr>
    </table>
    """
    scraper = HockeyScraper()
    result = scraper._parse_page(html)

    team = result[0]
    assert team["team_name"] == "Empty Team"
    assert team["ot_losses"] is None
    assert team["win_pct"] is None
    assert team["goals_for"] is None


def test_parse_page_sem_times_retorna_lista_vazia():
    scraper = HockeyScraper()
    result = scraper._parse_page("<table></table>")
    assert result == []
