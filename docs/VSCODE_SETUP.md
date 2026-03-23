# VS Code -pikaopas: Croppilaskuri-kehitys

## 1. Asenna perustarvikkeet

### Python
- Lataa: https://www.python.org/downloads/
- Windows: ruksaa "Add Python to PATH" asennusohjelmassa

### VS Code
- Lataa: https://code.visualstudio.com/
- Avaa VS Code ja asenna laajennukset (Extensions-paneeli, `Ctrl+Shift+X`):
  - **Python** (`ms-python.python`) — pakollinen
  - **Ruff** (`charliermarsh.ruff`) — automaattinen linting
  - **Mypy Type Checker** (`ms-python.mypy-type-checker`) — tyyppitarkistus
  - **GitLens** (`eamodio.gitlens`) — git-historia

## 2. Avaa projekti

```
Tiedosto → Avaa kansio → valitse Croppilaskuri-GUI/
```

VS Code tunnistaa automaattisesti `pyproject.toml`-tiedoston.

## 3. Luo virtuaaliympäristö

Avaa terminaali VS Codessa (`Ctrl+ö` tai `Ctrl+Shift+ö`):

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

VS Code kysyy: "We noticed a new environment..." → Klikkaa **Yes**.

## 4. Asenna riippuvuudet

```bash
pip install -e ".[dev]"
```

Tämä asentaa:
- PyQt5 (GUI-kirjasto)
- pytest (testit)
- ruff (linting)
- mypy (tyyppitarkistus)
- pre-commit (automaattiset tarkistukset)
- pyinstaller (.exe-buildi)

## 5. Testaa asennus

```bash
# Aja testit
pytest

# Aja sovellus
python -m croppilaskuri
```

## 6. VS Code -asetukset (suositus)

Luo tiedosto `.vscode/settings.json` projektikansioon:

```json
{
    "python.defaultInterpreterPath": ".venv/Scripts/python",
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": "explicit",
            "source.organizeImports.ruff": "explicit"
        }
    },
    "python.analysis.typeCheckingMode": "basic",
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".ruff_cache": true,
        ".mypy_cache": true
    }
}
```

## 7. Päivittäinen työnkulku

| Toiminto | Komento |
|----------|---------|
| Aja sovellus | `python -m croppilaskuri` |
| Aja testit | `pytest` |
| Tarkista linting | `ruff check src/` |
| Formatoi koodi | `ruff format src/` |
| Tarkista tyypit | `mypy src/` |
| Buildaa .exe | `python scripts/build_exe.py` |

## 8. Hyödyllisiä pikanäppäimiä

| Näppäin | Toiminto |
|---------|----------|
| `Ctrl+Shift+P` | Komentopalkki (command palette) |
| `F5` | Käynnistä debuggeri |
| `Ctrl+ö` | Avaa/sulje terminaali |
| `Ctrl+P` | Pikanavigaatio tiedostoihin |
| `F12` | Siirry funktion määrittelyyn |
| `Shift+F12` | Etsi funktion kaikki viittaukset |
| `Ctrl+Shift+F` | Etsi kaikista tiedostoista |

## Vaihtoehto: PyCharm

Jos haluat käyttää PyCharmin sijaan:
1. Lataa PyCharm Community (ilmainen): https://www.jetbrains.com/pycharm/
2. Avaa projektikansio
3. PyCharm tunnistaa `pyproject.toml`-tiedoston automaattisesti
4. Settings → Python Interpreter → lisää `.venv`-virtuaaliympäristö
5. PyCharm sisältää debuggerin, refaktorointityökalut ja testien ajajan valmiina
