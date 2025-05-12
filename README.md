# Croppilaskuri GUI (Eclipse Contouring Helper)

**Versio:** v0.2.2-alpha
**Päivitetty:** 12.5.2025

Tämä työkalu on suunniteltu avustamaan Eclipse™-sädehoitojärjestelmän käyttäjiä määrittelytyössä (contouring) luomalla vaiheittaisia ohjeita ja esimerkkejä optimointikriteereistä sädehoidon suunnittelua varten. Sovellus auttaa erityisesti monimutkaisempien PTV- ja OAR-rakenteiden (kuten dPTV, vOARcrop, dPTV+OAR, Ring/NT) luomisessa.

## Ominaisuudet

* **PTV-annosten syöttö:** Käyttäjä voi syöttää useita PTV-annostasoja (Gy).
* **OAR-hallinta:**
    * Tervekudosten (OAR) nimien syöttö automaattisella täydennyksellä yleisimmille nimille (laajennettu lista).
    * Mahdollisuus määrittää kullekin OAR:lle, minkä PTV-annostasojen kanssa `dPTV+OAR`-päällekkäisyysrakenne luodaan (konfiguroitava dialogi).
* **Automaattinen ohjeiden generointi:**
    * Luo vaiheittaisen, kuvitetun (emojit) ohjeen tarvittavien apurakenteiden luomiseksi Eclipseen.
    * Ohjeistaa mm. PTV/CTV-kopioinnissa, Boolean-operaatioissa (Union, Intersection) ja useissa Crop-operaatioissa (PTV-PTV, PTV-CTV, Ring/NT-PTV, OAR-PTV, dPTV-CTV, dPTV vs [dPTV+OAR], vNiska vs PTV/Body).
    * Luo ohjeet myös syötetyille OAReille (`vOARcrop`-rakenteet).
    * Luo ohjeet `dPTV+OAR`-työkalurakenteille OAR- ja PTV-taso kohtaisesti.
    * Sisältää valinnaisen ohjeen `vNiska`-rakenteen luomiseksi.
* **Optimointikriteerien ehdotukset:**
    * Generoi esimerkinomaiset optimointikriteerit (Upper/Lower) HTML-muodossa.
    * Kriteerit PTV-rakenteille säätyvät dynaamisesti sen mukaan, onko kyseiselle PTV-annostasolle määritelty `dPTV+OAR`-leikkauksia.
    * Sisältää ehdotukset myös `dPTV+OAR`, `vOARcrop`, `vPTVkaikki`, `vCTVkaikki` ja `Ring`/`NT`-rakenteille (käyttäjän valinnan mukaan).
    * Muistutus NTO (Normal Tissue Objective) -parametreista.
* **Vaiheittaisten ohjeiden haku:** Etsi ohjeista avainsanoilla ja navigoi osumien välillä.
* **Crop-yhteenveto:** Näyttää yhteenvedon kaikista lasketuista crop-marginaaleista (cm) omalla välilehdellään.
* **Muut valinnat:**
    * Valinta Ring-rakenteen nimelle (`Ring` vai `NT`).
    * Valinta `dPTV+OAR` -rakenteen crop-marginaalille (0.5 mm vai 1.0 mm).
* **Käyttöliittymä:**
    * Graafinen käyttöliittymä rakennettu PyQt5-kirjastolla.
    * Ohjeet, kriteerit ja crop-yhteenveto näytetään omilla välilehdillään.
    * Mahdollisuus merkitä ohjeiden vaiheita tehdyksi, jolloin ne minimoituvat ja etenemistä voi seurata.

## Asennus ja käyttö (jaettavalle .exe-tiedostolle)

1.  Lataa uusin `Croppilaskuri_GUI_[versio].exe` -tiedosto [GitHub Releases -sivulta](https://github.com/RisDicom/Croppilaskuri-GUI/releases) (Linkki lisättävä, kun julkaisu on tehty).
2.  Suorita `.exe`-tiedosto. Erillistä asennusta ei tarvita.

## Kehitys

Tämä projekti on kehitetty Pythonilla ja PyQt5-kirjastolla graafista käyttöliittymää varten.

### Tarvittavat kirjastot (jos ajat lähdekoodista)

* Python 3.x
* PyQt5

Voit asentaa tarvittavat kirjastot esimerkiksi Pip-työkalulla:
`pip install PyQt5`

### Lähdekoodin ajaminen

1.  Kloonaa tai lataa repositorio: `git clone https://github.com/RisDicom/Croppilaskuri-GUI.git`
2.  Siirry projektihakemistoon: `cd Croppilaskuri-GUI`
3.  Varmista, että sinulla on Python ja PyQt5 asennettuna.
4.  Suorita pääohjelmatiedosto (`Croplaskuri_gui.py`) Python-tulkin kautta: `python Croplaskuri_gui.py`

## Huomioitavaa

* **Tämä on alpha-vaiheen ohjelmisto.** Se saattaa sisältää bugeja tai keskeneräisiä ominaisuuksia. Käytä harkiten ja tarkista aina generoituja ohjeita ja kriteereitä huolellisesti suhteessa paikallisiin hoitoprotokolliin.
* Ohjelman antamat optimointikriteerit ovat **esimerkkejä** ja ne tulee aina sovittaa potilaskohtaisesti ja laitoksen omien käytäntöjen mukaisesti.
* Eclipse™ on Varian Medical Systems, Inc:n rekisteröity tavaramerkki. Tämä työkalu on itsenäisesti kehitetty eikä se ole Varianin hyväksymä tai tukema.

## Tekijä

* Risto Hirvilammi (RisDicom)

## Lisenssi

Tämä projekti on lisensoitu MIT-lisenssillä. Katso `LICENSE`-tiedostoa lisätietoja varten.
