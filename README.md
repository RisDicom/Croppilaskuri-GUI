# Croppilaskuri GUI (Eclipse Contouring Helper)

**Versio:** v0.4.0  
**Päivitetty:** 2025

Työkalu Eclipse™-sädehoitojärjestelmän käyttäjille: luo vaiheittaisia ohjeita
ja esimerkkejä optimointikriteereistä sädehoidon suunnittelua varten.

## Pikastartti

### Vaihtoehto A: Lataa valmis .exe

Lataa uusin release [GitHub Releases -sivulta](https://github.com/RisDicom/Croppilaskuri-GUI/releases).

### Vaihtoehto B: Aja lähdekoodista

```bash
# 1. Kloonaa
git clone https://github.com/RisDicom/Croppilaskuri-GUI.git
cd Croppilaskuri-GUI

# 2. Luo virtuaaliympäristö
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Asenna
pip install -e .

# 4. Käynnistä
croppilaskuri
# tai:
python -m croppilaskuri
```

## Kehitysympäristö

### Suositellut työkalut

| Työkalu | Tarkoitus | Asennus |
|---------|-----------|---------|
| **VS Code** | Editori/IDE | [code.visualstudio.com](https://code.visualstudio.com) |
| **Python-laajennus** | Kielituki | VS Code Extensions: `ms-python.python` |
| **Ruff-laajennus** | Linting + formatointi | VS Code Extensions: `charliermarsh.ruff` |
| **Python 3.10+** | Tulkki | [python.org](https://python.org) |

### Kehitysasennus

```bash
# Asenna kehitysriippuvuudet
pip install -e ".[dev]"

# Asenna pre-commit hookit (tarkistaa koodin automaattisesti)
pre-commit install

# Aja testit
pytest

# Tarkista koodi manuaalisesti
ruff check src/ tests/
ruff format src/ tests/
mypy src/
```

### .exe-buildi

```bash
python scripts/build_exe.py
# → dist/Croppilaskuri_GUI.exe
```

## Projektirakenne

```
src/croppilaskuri/
├── __main__.py          # Käynnistyspiste
├── config/
│   ├── constants.py     # Vakiot, värit, emojit
│   └── oar_data.py      # OAR-nimilistat
├── core/
│   ├── calculations.py  # Puhtaat laskentafunktiot
│   ├── guide_logic.py   # Ohjeiden generointi
│   └── optimization_criteria.py  # Kriteerien HTML
├── ui/
│   ├── main_window.py   # Pääikkuna (orkestroija)
│   ├── styles.py        # Qt-tyylitaulukko
│   ├── panels/
│   │   ├── dose_panel.py   # PTV-annostasosyöttö
│   │   └── oar_panel.py    # OAR-hallintapaneeli
│   └── widgets/
│       ├── step_widget.py  # Vaihekortti-widget
│       └── oar_dialog.py   # Overlap-asetusdialogi
└── utils/
    └── text.py           # HTML-apufunktiot
```

**Suunnitteluperiaatteet:**
- `core/` ei riipu `ui/`-paketista → testattavissa ilman GUI:ta
- `config/` sisältää vain dataa, ei logiikkaa
- `ui/panels/` ovat itsenäisiä widgettejä jotka kommunikoivat signaaleilla
- Kaikki CSS yhdessä paikassa (`styles.py`)

## Huomioitavaa

- **Alpha-vaiheen ohjelmisto.** Tarkista generoidut ohjeet aina paikallisten
  hoitoprotokollien mukaan.
- Optimointikriteerit ovat **esimerkkejä** — sovita potilaskohtaisesti.
- Eclipse™ on Varian Medical Systems, Inc:n rekisteröity tavaramerkki.

## Tekijä

Risto Hirvilammi (RisDicom)

## Lisenssi

MIT – katso [LICENSE](LICENSE).
