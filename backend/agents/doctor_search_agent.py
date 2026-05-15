import time
import re
import requests
from bs4 import BeautifulSoup
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from config.settings import settings
from agents.state import AgentState

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Correct URL slugs from med.tn (e.g. med.tn/medecin/nutritionniste)
SPECIALTY_MAP = {
    "nutritionist":    "nutritionniste",
    "nutrition":       "nutritionniste",
    "nutritionniste":  "nutritionniste",
    "diabetologist":   "endocrinologue-diabetologue",
    "diabétologue":    "endocrinologue-diabetologue",
    "diabetes":        "endocrinologue-diabetologue",
    "endocrinologist": "endocrinologue-diabetologue",
    "endocrinologue":  "endocrinologue-diabetologue",
    "general":         "medecin-generaliste",
    "généraliste":     "medecin-generaliste",
    "cardiologue":     "cardiologue",
    "cardiology":      "cardiologue",
    "dermatologue":    "dermatologue",
    "gynécologue":     "gynecologue",
    "pédiatre":        "pediatre",
    "psychiatre":      "psychiatre",
}

CITY_MAP = {
    "tunis":     "Tunis",
    "sfax":      "Sfax",
    "sousse":    "Sousse",
    "ariana":    "Ariana",
    "ben arous": "Ben-arous",
    "monastir":  "Monastir",
    "nabeul":    "Nabeul",
    "bizerte":   "Bizerte",
    "gafsa":     "Gafsa",
    "manouba":   "Mannouba",
    "mahdia":    "Mahdia",
}

BASE_URL = "https://med.tn"

SUMMARIZE_PROMPT = """You are a helpful medical assistant for Tunisia.
The user is looking for a doctor in Tunisia.
Here are the doctors found on med.tn:

{doctors_text}

Summarize this list in a friendly, clear way in French.
For each doctor mention: name, specialty, location, and that they can book on med.tn.
If no doctors were found, tell the user politely and suggest they visit med.tn directly."""


# ─── Helpers ──────────────────────────────────────────────────────────────────

def detect_specialty(query: str) -> str:
    """Detect which specialty slug to use from the user query."""
    q = query.lower()
    for keyword, slug in SPECIALTY_MAP.items():
        if keyword in q:
            return slug
    return "nutritionniste"  # default


def detect_city(query: str) -> str:
    """Detect city name from the user query."""
    q = query.lower()
    for keyword, city in CITY_MAP.items():
        if keyword in q:
            return city
    return ""


def build_url(specialty_slug: str, city: str = "", page: int = 1) -> str:
    """Build the correct med.tn listing URL."""
    url = f"{BASE_URL}/medecin/{specialty_slug}"
    params = []
    if city:
        params.append(f"ville={city}")
    if page > 1:
        params.append(f"page={page}")
    if params:
        url += "?" + "&".join(params)
    return url


# ─── Scraping ─────────────────────────────────────────────────────────────────

def scrape_with_requests(url: str) -> str | None:
    """Try scraping with plain requests first (faster)."""
    try:
        session = requests.Session()
        session.get(BASE_URL, headers=HEADERS, timeout=10)  # get cookies
        resp = session.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200 and len(resp.text) > 500:
            return resp.text
    except Exception as e:
        print(f"[DoctorSearch] requests failed: {e}")
    return None


def scrape_with_selenium(url: str, wait: float = 3.0) -> str:
    """Fallback: use Selenium if requests is blocked."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument(f"user-agent={HEADERS['User-Agent']}")

    try:
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
    except Exception:
        driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div#search_listing, main, body")
                )
            )
        except Exception:
            pass
        time.sleep(wait)
        return driver.page_source
    finally:
        driver.quit()


def parse_doctors(html: str, specialty_slug: str) -> list[dict]:
    """Parse doctor cards from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    doctors = []

    # Target the main listing container
    listing = (
        soup.find("div", id="search_listing") or
        soup.find("div", class_=re.compile(r"loader.search|search.result", re.I)) or
        soup.find("main") or
        soup
    )

    # Try known card selectors
    cards = (
        listing.find_all("div", class_=re.compile(r"bottom.box|doctor.item|medecin.card", re.I)) or
        listing.find_all("article") or
        listing.find_all("div", class_=re.compile(r"listing.item|result.item|pf-item", re.I))
    )

    for card in cards[:8]:  # max 8 results
        try:
            # Name
            name_el = (
                card.find("a", class_=re.compile(r"name|doctor|titre|title", re.I)) or
                card.find(["h2", "h3", "h4"]) or
                card.find("a", href=re.compile(r"/medecin/"))
            )
            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            if len(name) < 4 or "rendez" in name.lower():
                continue

            # Profile link
            link_el = name_el if name_el.name == "a" else name_el.find("a")
            href = link_el["href"] if link_el and link_el.get("href") else ""
            link = (BASE_URL + href) if href.startswith("/") else href or BASE_URL

            # Specialty
            spec_el = card.find(class_=re.compile(r"spec|specialit", re.I))
            specialty = spec_el.get_text(strip=True) if spec_el else specialty_slug

            # Location
            loc_el = card.find(class_=re.compile(r"locat|address|adresse|city|ville", re.I))
            location = loc_el.get_text(strip=True) if loc_el else "Tunisie"

            # Tags / competences
            tags = [
                t.get_text(strip=True)
                for t in card.find_all(["span", "a"])
                if "tag" in " ".join(t.get("class", [])).lower()
                and len(t.get_text(strip=True)) > 2
            ]

            doctors.append({
                "name":      name,
                "specialty": specialty,
                "location":  location,
                "tags":      tags[:4],
                "link":      link,
            })

        except Exception:
            continue

    # Fallback: extract Dr. names from anchor tags
    if not doctors:
        for a in listing.find_all("a", href=re.compile(r"/medecin/[a-z]")):
            name = a.get_text(strip=True)
            if re.search(r"\bdr\.?\b", name, re.I) and len(name) > 4:
                href = a["href"]
                doctors.append({
                    "name":      name,
                    "specialty": specialty_slug,
                    "location":  "Tunisie",
                    "tags":      [],
                    "link":      (BASE_URL + href) if href.startswith("/") else href,
                })

    return doctors


def scrape_medtn(specialty_slug: str, city: str = "") -> list[dict]:
    """
    Main scraping function.
    Tries requests first, falls back to Selenium if blocked.
    """
    url = build_url(specialty_slug, city)
    print(f"[DoctorSearch] URL → {url}")

    # Try fast path first
    html = scrape_with_requests(url)
    source = "requests"

    if not html:
        print("[DoctorSearch] requests blocked → switching to Selenium")
        html = scrape_with_selenium(url)
        source = "selenium"

    doctors = parse_doctors(html, specialty_slug)
    print(f"[DoctorSearch] {len(doctors)} doctor(s) found via {source}")
    return doctors


def format_doctors_text(doctors: list, specialty: str) -> str:
    """Format doctor list as readable text for the LLM."""
    if not doctors:
        return f"No doctors found for '{specialty}' on med.tn."

    lines = [f"Found {len(doctors)} doctor(s) for '{specialty}':\n"]
    for i, d in enumerate(doctors, 1):
        tags = ", ".join(d["tags"]) if d["tags"] else "—"
        lines.append(
            f"{i}. {d['name']} — {d['specialty']} — {d['location']}\n"
            f"   Compétences: {tags}\n"
            f"   Profil: {d['link']}"
        )
    return "\n".join(lines)


# ─── Agent ────────────────────────────────────────────────────────────────────

class DoctorSearchAgent:
    def __init__(self):
        self.llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=0.3,
        )

    def run(self, state: AgentState) -> AgentState:
        query = state["query"]

        # 1. Detect specialty + city from query
        specialty_slug = detect_specialty(query)
        city           = detect_city(query)
        print(f"[DoctorSearch] Specialty: {specialty_slug} | City: {city or 'all Tunisia'}")

        # 2. Scrape med.tn — always
        doctors = scrape_medtn(specialty_slug, city)

        # 3. Format + LLM summary
        doctors_text = format_doctors_text(doctors, specialty_slug)
        prompt = SUMMARIZE_PROMPT.format(doctors_text=doctors_text)
        response = self.llm.invoke([HumanMessage(content=prompt)])

        suffix = (
            f"\n\n🔗 Rechercher sur med.tn : {build_url(specialty_slug, city)}"
            if not doctors else
            f"\n\n🔗 Prendre rendez-vous sur : {BASE_URL}"
        )
        answer = response.content + suffix

        return {**state, "answer": answer, "doctors": doctors}


doctor_search_agent = DoctorSearchAgent()