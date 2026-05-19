# RSS Reader & News Analyzer

>  Tässä työssä on käytetty ChatGPT:tä !

Modulaarinen Python-pohjainen RSS-lukija ja uutisanalysoija, joka hakee, tallentaa, kategorisoi ja analysoi uutisartikkeleita useista RSS-syötteistä SQLite-tietokantaan.

Projekti on toteutettu osana ohjelmistokehityksen ja kyberturvallisuuden opiskelua. Sovellus keskittyy erityisesti automaatioon, modulaariseen arkkitehtuuriin, tietokantoihin, tekstin käsittelyyn sekä käytännön backend-kehitykseen Pythonilla.

---

# Ominaisuudet

- RSS-syötteiden automaattinen haku
- Artikkelien tallennus SQLite-tietokantaan
- Duplikaattiartikkelien esto
- Artikkelien automaattinen tagitus avainsanojen perusteella
- Suosikkiartikkelien tunnistus
- Hakutoiminto avainsanoilla
- Artikkelien selaus tagien perusteella
- Yleisimpien sanojen analysointi
- Yleisimpien kategorioiden analysointi
- Ajastettu automaattinen päivitys
- Tietokannan varmuuskopiointi
- Loki-/logging-järjestelmä
- Suomen- ja englanninkielisten stop-sanojen suodatus

---

# Käytetyt teknologiat

- Python
- SQLite
- RSS / Feed Parsing
- BeautifulSoup4
- NLTK
- Logging
- JSON-konfiguraatiot

## Kirjastot

- feedparser
- beautifulsoup4
- nltk
- sqlite3

---

# Toimintaperiaate

1. RSS-syötteet ladataan `config.json`-tiedostosta
2. Artikkelit haetaan ja puhdistetaan HTML-sisällöstä
3. Artikkelit kategorisoidaan ja tagitetaan
4. Tiedot tallennetaan SQLite-tietokantaan
5. Duplikaatit estetään automaattisesti
6. Käyttäjä voi analysoida ja hakea artikkeleita

---

# Tekijä

Kimi Kyrölä
