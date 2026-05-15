"""
med.tn Scraper — Recherche de médecins et nutritionnistes
Supporte: Selenium (avec JS) + BeautifulSoup (parsing HTML)
"""

import time
import re
from dataclasses import dataclass, field, asdict
from typing import Optional
import json

# ─── Data Model ────────────────────────────────────────────────────────────────

@dataclass
class Medecin:
    nom: str
    specialite: str
    ville: str
    adresse: str
    tags: list[str] = field(default_factory=list)
    conventionné_cnam: bool = False
    visite_domicile: bool = False
    url_profil: str = ""

    def to_dict(self):
        return asdict(self)

    def __str__(self):
        tags_str = ", ".join(self.tags) if self.tags else "—"
        cnam = "✓ CNAM" if self.conventionné_cnam else ""
        domicile = "✓ Domicile" if self.visite_domicile else ""
        extras = " | ".join(filter(None, [cnam, domicile]))
        return (
            f"👨‍⚕️ {self.nom}\n"
            f"   Spécialité : {self.specialite}\n"
            f"   📍 {self.adresse}, {self.ville}\n"
            f"   🏷️  {tags_str}\n"
            + (f"   ℹ️  {extras}\n" if extras else "")
            + (f"   🔗 {self.url_profil}\n" if self.url_profil else "")
        )


# ─── URL Builder ───────────────────────────────────────────────────────────────

SPECIALTY_SLUGS = {
    # Nutrition & diabète
    "nutritionniste":             "nutritionniste",
    "diététicien":                "dieteticien-nutritionniste",
    "diabétologue":               "endocrinologue-diabetologue",
    "endocrinologue":             "endocrinologue-diabetologue",
    # Autres spécialités courantes
    "généraliste":                "medecin-generaliste",
    "cardiologue":                "cardiologue",
    "dermatologue":               "dermatologue",
    "gastroentérologue":          "gastroenterologue",
    "gynécologue":                "gynecologue",
    "neurologue":                 "neurologue",
    "ophtalmologue":              "ophtalmologue",
    "pédiatre":                   "pediatre",
    "psychiatre":                 "psychiatre",
    "radiologue":                 "radiologue",
    "rhumatologue":               "rhumatologue",
    "urologue":                   "urologue",
}

CITY_SLUGS = {
    "tunis":      "Tunis",
    "sfax":       "Sfax",
    "sousse":     "Sousse",
    "ariana":     "Ariana",
    "ben arous":  "Ben-arous",
    "monastir":   "Monastir",
    "nabeul":     "Nabeul",
    "bizerte":    "Bizerte",
    "gafsa":      "Gafsa",
    "kairouan":   "Kairouan",
    "manouba":    "Mannouba",
    "mahdia":     "Mahdia",
}

BASE_URL = "https://med.tn"

def build_url(specialite: str, ville: Optional[str] = None, page: int = 1) -> str:
    """Construit l'URL de recherche med.tn."""
    # Normaliser la spécialité
    slug = specialite.lower().strip()
    for key, val in SPECIALTY_SLUGS.items():
        if key in slug or slug in key:
            slug = val
            break

    url = f"{BASE_URL}/medecin/{slug}"

    params = []
    if ville:
        ville_lower = ville.lower().strip()
        for key, val in CITY_SLUGS.items():
            if key in ville_lower:
                params.append(f"ville={val}")
                break
        else:
            params.append(f"ville={ville.capitalize()}")

    if page > 1:
        params.append(f"page={page}")

    if params:
        url += "?" + "&".join(params)

    return url


# ─── Selenium Scraper ──────────────────────────────────────────────────────────

def get_driver(headless: bool = True):
    """
    Initialise un driver Chrome/Chromium.
    Installe chromedriver si nécessaire via webdriver-manager.
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    try:
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
    except Exception:
        service = None

    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(service=service, options=options) if service \
        else webdriver.Chrome(options=options)
    return driver


def parse_doctor_cards(soup) -> list[Medecin]:
    """Parse les cartes médecins depuis un objet BeautifulSoup."""
    from bs4 import BeautifulSoup
    medecins = []

    # Les cartes médecins sont dans des divs avec bottom_box ou doctor-item
    # Structure observée sur med.tn :
    cards = (
        soup.find_all("div", class_=re.compile(r"bottom[_-]box", re.I)) or
        soup.find_all("div", class_=re.compile(r"doctor[_-]item", re.I)) or
        soup.find_all("article", class_=re.compile(r"medecin|doctor|listing", re.I)) or
        soup.find_all("div", class_=re.compile(r"listing[_-]item|search[_-]item", re.I))
    )

    # Fallback: chercher par structure (nom en lien bleu + spécialité + localisation)
    if not cards:
        cards = soup.find_all("div", class_=re.compile(r"pf-", re.I))

    for card in cards:
        try:
            # Nom du médecin
            nom_el = (
                card.find("a", class_=re.compile(r"name|doctor|medecin|titre|title", re.I)) or
                card.find("h2") or card.find("h3") or card.find("h4") or
                card.find("a", href=re.compile(r"/medecin/|/doctor/"))
            )
            if not nom_el:
                continue
            nom = nom_el.get_text(strip=True)
            if len(nom) < 3 or nom.lower() in ("voir plus", "prendre rendez-vous"):
                continue

            # Lien profil
            url_profil = ""
            link = nom_el if nom_el.name == "a" else nom_el.find("a")
            if link and link.get("href"):
                href = link["href"]
                url_profil = href if href.startswith("http") else BASE_URL + href

            # Spécialité
            spec_el = card.find(class_=re.compile(r"spec|specialit|type", re.I))
            specialite = spec_el.get_text(strip=True) if spec_el else "Non précisé"

            # Adresse / Ville
            loc_el = (
                card.find(class_=re.compile(r"locat|address|adresse|city|ville", re.I)) or
                card.find("i", class_=re.compile(r"map|pin|location", re.I))
            )
            adresse_full = loc_el.get_text(strip=True) if loc_el else ""
            parts = [p.strip() for p in adresse_full.split(",") if p.strip()]
            adresse = ", ".join(parts[:-1]) if len(parts) > 1 else adresse_full
            ville = parts[-1] if parts else ""

            # Tags / compétences
            tags_container = card.find(class_=re.compile(r"tag|skill|competence|keyword", re.I))
            tags = []
            if tags_container:
                for tag in tags_container.find_all(["span", "a", "li"]):
                    t = tag.get_text(strip=True)
                    if t and len(t) > 2:
                        tags.append(t)
            else:
                # Chercher tous les spans qui ressemblent à des tags
                for span in card.find_all("span"):
                    cls = " ".join(span.get("class", []))
                    if "tag" in cls.lower() or "badge" in cls.lower():
                        t = span.get_text(strip=True)
                        if t:
                            tags.append(t)

            medecins.append(Medecin(
                nom=nom,
                specialite=specialite,
                ville=ville,
                adresse=adresse,
                tags=tags[:6],
                url_profil=url_profil,
            ))

        except Exception:
            continue

    return medecins


def scrape_medecins(
    specialite: str,
    ville: Optional[str] = None,
    max_pages: int = 2,
    headless: bool = True,
    wait_time: float = 3.0,
) -> list[Medecin]:
    """
    Scrape les médecins de med.tn pour une spécialité et ville données.

    Args:
        specialite: ex. "nutritionniste", "diabétologue", "cardiologue"
        ville: ex. "Tunis", "Sfax", "Sousse" (optionnel)
        max_pages: nombre de pages à parcourir (défaut 2)
        headless: mode sans fenêtre (défaut True)
        wait_time: délai d'attente après chargement de page

    Returns:
        Liste d'objets Medecin
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from bs4 import BeautifulSoup

    all_medecins: list[Medecin] = []
    driver = get_driver(headless=headless)

    try:
        for page in range(1, max_pages + 1):
            url = build_url(specialite, ville, page)
            print(f"  📄 Page {page} → {url}")

            driver.get(url)

            # Attendre que les résultats se chargent
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div#search_listing, div.loader-search, main")
                    )
                )
            except Exception:
                pass

            time.sleep(wait_time)  # Laisser le JS finir

            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            # Chercher les cartes médecin dans le listing principal
            listing = (
                soup.find("div", id="search_listing") or
                soup.find("div", class_=re.compile(r"loader.search|search.result|listing", re.I)) or
                soup.find("main") or
                soup
            )

            page_medecins = parse_doctor_cards(listing)

            if not page_medecins:
                # Dernier recours : extraire manuellement les noms de médecins (Dr. ...)
                page_medecins = _fallback_parse(soup, specialite)

            if not page_medecins:
                print(f"  ⚠️  Aucun résultat page {page}, arrêt.")
                break

            all_medecins.extend(page_medecins)
            print(f"  ✅ {len(page_medecins)} médecin(s) trouvés page {page}")

            # Vérifier s'il y a une page suivante
            next_btn = soup.find("a", class_=re.compile(r"next|suivant", re.I))
            if not next_btn and page < max_pages:
                print("  ℹ️  Pas de page suivante.")
                break

    finally:
        driver.quit()

    # Dédoublonner par nom
    seen = set()
    unique = []
    for m in all_medecins:
        key = m.nom.lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(m)

    return unique


def _fallback_parse(soup, specialite: str) -> list[Medecin]:
    """
    Méthode de secours : cherche les noms de docteurs (Dr. ...) dans tout le HTML
    et reconstruit des objets Medecin approximatifs.
    """
    medecins = []
    # Trouver tous les liens qui ressemblent à des profils de médecins
    for a in soup.find_all("a", href=re.compile(r"/medecin/[a-z]")):
        nom = a.get_text(strip=True)
        if not nom or len(nom) < 5:
            continue
        if not re.search(r"\bdr\.?\b", nom, re.I):
            continue
        href = a["href"]
        url_profil = href if href.startswith("http") else BASE_URL + href

        # Chercher la ville dans l'environnement du lien
        parent = a.find_parent("div") or a.find_parent("article")
        adresse = ""
        if parent:
            loc = parent.find(class_=re.compile(r"locat|address|city", re.I))
            adresse = loc.get_text(strip=True) if loc else ""

        medecins.append(Medecin(
            nom=nom,
            specialite=specialite.capitalize(),
            ville="",
            adresse=adresse,
            url_profil=url_profil,
        ))

    return medecins


# ─── CLI rapide ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    specialite = sys.argv[1] if len(sys.argv) > 1 else "nutritionniste"
    ville      = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"\n🔍 Recherche : {specialite}" + (f" à {ville}" if ville else " en Tunisie"))
    print("─" * 60)

    resultats = scrape_medecins(specialite, ville, max_pages=2)

    if not resultats:
        print("❌ Aucun résultat trouvé.")
    else:
        print(f"\n📋 {len(resultats)} médecin(s) trouvé(s) :\n")
        for i, m in enumerate(resultats, 1):
            print(f"{i}. {m}")

    # Sauvegarder en JSON
    output_file = f"medecins_{specialite.replace(' ', '_')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump([m.to_dict() for m in resultats], f, ensure_ascii=False, indent=2)
    print(f"\n💾 Résultats sauvegardés dans {output_file}")
