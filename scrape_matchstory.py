import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

WHOSCORED_URL = "https://www.whoscored.com"

def scrape_match_story(game_id: int, wait_s: int = 10) -> dict:
    url = f"{WHOSCORED_URL}/Matches/{game_id}/MatchReport"
    driver = webdriver.Chrome()
    driver.get(url)

    try:
        WebDriverWait(driver, wait_s).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tr.matchstory-typeheader"))
        )
    except Exception:
        print("⚠️ Nie znaleziono sekcji Match Story")
        driver.quit()
        return {}

    soup = BeautifulSoup(driver.page_source, "lxml")
    driver.quit()

    out = {
        "home_strengths": [],
        "away_strengths": [],
        "home_weaknesses": [],
        "away_weaknesses": [],
        "home_styles": [],
        "away_styles": [],
    }

    def _cell_items(td):
        items = []
        for span in td.select("div.matchstory-icon span.matchstory-text"):
            txt = span.get_text(strip=True)
            if txt and "no significant" not in txt.lower():
                items.append(txt)
        raw = td.get_text(strip=True)
        if raw and "no significant" not in raw.lower() and raw not in items:
            items.append(raw)
        return items

    current = None
    section_map = {"strength": "strengths", "weakness": "weaknesses", "style": "styles"}

    for tr in soup.select("tr.matchstory-typeheader, tr.matchstory-row"):
        classes = tr.get("class", [])
        if "matchstory-typeheader" in classes:
            header = tr.get_text(" ", strip=True).lower()
            current = None
            for key, val in section_map.items():
                if key in header:
                    current = val
                    break
        elif "matchstory-row" in classes and current is not None:
            tds = tr.find_all("td")
            if len(tds) >= 2:
                home_items = _cell_items(tds[0])
                away_items = _cell_items(tds[1])
                out[f"home_{current}"].extend(home_items)
                out[f"away_{current}"].extend(away_items)

    # usuwamy duplikaty
    for k, vals in out.items():
        seen, deduped = set(), []
        for v in vals:
            if v not in seen:
                seen.add(v)
                deduped.append(v)
        out[k] = deduped

    return out


if __name__ == "__main__":
    game_id = 1821232  # Arsenal - Man Utd
    data = scrape_match_story(game_id)
    print("\n=== WYNIK ===")
    for k, v in data.items():
        print(f"{k}: {v}")
