# Croppilaskuri GUI (Eclipse Contouring Helper)

**Versio:** v0.1.0-alpha 
**Päivitetty:** 9.5.2025

Tämä työkalu on suunniteltu avustamaan Eclipse™-sädehoitojärjestelmän käyttäjiä määrittelytyössä (contouring) luomalla vaiheittaisia ohjeita ja esimerkkejä optimointikriteereistä sädehoidon suunnittelua varten. Sovellus auttaa erityisesti monimutkaisempien PTV- ja OAR-rakenteiden (kuten dPTV, vOARcrop, dPTV+OAR) luomisessa.

## Ominaisuudet

* **PTV-annosten syöttö:** Käyttäjä voi syöttää useita PTV-annostasoja.
* **OAR-hallinta:**
    * Tervekudosten (OAR) nimien syöttö automaattisella täydennyksellä.
    * Mahdollisuus määrittää kullekin OAR:lle, minkä PTV-annostasojen kanssa `dPTV+OAR`-päällekkäisyysrakenne luodaan.
* **Automaattinen ohjeiden generointi:**
    * Luo vaiheittaisen, kuvitetun (emojit) ohjeen tarvittavien apurakenteiden luomiseksi Eclipseen.
    * Ohjeistaa mm. PTV/CTV-kopioinnissa, crop-operaatioissa, Ring-rakenteiden luonnissa ja dPTV-rakenteiden muodostamisessa.
    * Luo ohjeet myös syötetyille OAReille (esim. `vRectumCrop`).
    * Luo ohjeet `dPTV+OAR`-rakenteille OAR- ja PTV-taso kohtaisesti.
    * Sisältää valinnaisen ohjeen `vNiska`-rakenteen luomiseksi.
* **Optimointikriteerien ehdotukset:**
    * Generoi esimerkinomaiset optimointikriteerit (Upper/Lower) HTML-muodossa.
    * Kriteerit PTV-rakenteille säätyvät dynaamisesti sen mukaan, onko kyseiselle PTV-annostasolle määritelty `dPTV+OAR`-leikkauksia.
    * Sisältää ehdotukset myös `dPTV+OAR`, `vOARcrop`, `vPTVkaikki`, `vCTVkaikki` ja `Ring`-rakenteille.
    * Muistutus NTO (Normal Tissue Objective) -parametreista.
* **Käyttöliittymä:**
    * Graafinen käyttöliittymä rakennettu PyQt5-kirjastolla.
    * Ohjeet ja kriteerit näytetään omilla välilehdillään.
    * Mahdollisuus merkitä ohjeiden vaiheita tehdyksi, jolloin ne minimoituvat.

## Asennus ja käyttö (jaettavalle .exe-tiedostolle)

1.  Lataa uusin `Croppilaskuri GUI.exe` -tiedosto [GitHub Releases -sivulta](https://github.com/rijohi/Croppilaskuri-GUI/releases)
2.  Suorita `.exe`-tiedosto. Erillistä asennusta ei tarvita.

## Kehitys

Tämä projekti on kehitetty Pythonilla ja PyQt5-kirjastolla graafista käyttöliittymää varten.

### Tarvittavat kirjastot (jos ajat lähdekoodista)

* Python 3.x
* PyQt5

Voit asentaa tarvittavat kirjastot esimerkiksi Pip-työkalulla:
`pip install PyQt5`

### Lähdekoodin ajaminen

1.  Kloonaa tai lataa repositorio.
2.  Varmista, että sinulla on Python ja PyQt5 asennettuna.
3.  Suorita pääohjelmatiedosto (esim. `Croplaskuri_gui.py`) Python-tulkin kautta:
    `python Croplaskuri_gui.py`

## Huomioitavaa

* **Tämä on alpha-vaiheen ohjelmisto.** Se saattaa sisältää bugeja tai keskeneräisiä ominaisuuksia. Käytä harkiten ja tarkista aina generoituja ohjeita ja kriteereitä huolellisesti suhteessa paikallisiin hoitoprotokolliin.
* Ohjelman antamat optimointikriteerit ovat **esimerkkejä** ja ne tulee aina sovittaa potilaskohtaisesti ja laitoksen omien käytäntöjen mukaisesti.
* Eclipse™ on Varian Medical Systems, Inc:n rekisteröity tavaramerkki. Tämä työkalu on itsenäisesti kehitetty eikä se ole Varianin hyväksymä tai tukema.

## Tekijä

* Risto Hirvilammi (rijohi)

## Lisenssi

Tämä projekti on lisensoitu MIT-lisenssillä. Katso `LICENSE`-tiedostoa lisätietoja varten.
(Sinun tulee luoda myös `LICENSE`-niminen tiedosto projektisi juureen, joka sisältää MIT-lisenssin tekstin.)
