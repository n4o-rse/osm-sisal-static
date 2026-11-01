# PRIMER — osm-sisal-static

Arbeitsplan für `n4o-rse/osm-sisal-static` (Repo-Name: Vorschlag 2026-11-01). Wird zu Beginn jedes Chats hochgeladen (Bundle, siehe A5) und am Ende zurückgeschrieben. Stand: 2026-11-01 (S0: Festlegungen, Befunde; S1: Skeleton; S2: Modell aus `osm-benchmarks-static`).

Sprache: dieses Dokument ist deutsch, alles andere im Repo (Code, Kommentare, README) ist britisches Englisch.

---

## Teil A — Immer gültig

### A1 Ausgangslage

| Repo | Rolle | Stand |
|---|---|---|
| `Research-Squirrel-Engineers/osm2lod` | Prototyp: Overpass-Abfrage je Export-Typ, CSV, TTL und QuickStatements je Lauf; liefert hier die Abfragen | vorhanden, wird nicht umgebaut |
| `n4o-rse/wikibase-static` | Paket (v0.24.1): CSV (vier Tabellen) → Wikibase-JSON → Seiten, RDF, SPARQL; Verb `import-osm`; BeaverBridge-Design mit hell/dunkel | vorhanden; Änderungen für dieses Repo: S3 |
| `n4o-rse/osm-benchmarks-static` | Vorbild: Site-Repo mit den Benchmarks (23 Nodes, live); Modell, Skeleton, Workflow, Abfragen werden von dort übernommen | vorhanden, S0 bis S8 erledigt |
| `n4o-rse/osm-sisal-static` | dieses Repo | neu, S0 bis S2 gebaut |
| `n4o-rse/osm-holywells-static`, `n4o-rse/osm-ogham-static` | Schwester-Sites für Holy Wells und Ogham-Steine (gleiches Modell) | neu, werden gleichzeitig angelegt |
| `py/SISAL/` in osm2lod | Zuordnung der SISAL-Standorte zu OSM-Höhlen (Skripte, Notebooks, CSV, ID-Listen); `sisal_sites_all.csv` mit 305 Standorten | vorhanden, wird nur gelesen |

Nicht neu zu bauen: das Modell (P100 bis P113), `import-osm`, Seiten, RDF, SPARQL-Seite, `check-crm` (kommen aus `osm-benchmarks-static` und dem Paket).

**Befunde** (geprüft 2026-11-01, soweit nicht anders gesagt):

1. **osm2lod, Ist-Stand `sisal`** (Lauf 2026-03-28, `dist/2026-03-28/`): 219 Elemente, alle Nodes, alle mit `natural=cave_entrance` (38 davon auch `tourism=attraction`, einer `tourism=viewpoint`). Summe der aktuellen Versionsnummern 649 (höchste Version 27); 184 von 219 mit `name`, 64 mit `wikidata`, 14 mit `wikimedia_commons`. Anders als bei den Benchmarks, Holy Wells und Ogham-Steinen ist die Menge **keine Gebiets- und Tag-Abfrage**, sondern eine feste Liste von OSM-IDs.
2. **Die Abfrage** (aus `metadata_sisal_2026-03-28_*.json`, identisch mit `py/SISAL/output/osm_ids_list.py`): 221 Zeilen `node(<id>);`, `out meta;` und 180 s hier (dort `out meta geom;` und 25 s). Die Datei steht unter `data/seeds/overpass-sisal.overpassql`. Zwei der 221 IDs fehlen im Lauf vom 2026-03-28 (13581390702 und 13586189099); warum (gelöscht oder noch nicht vorhanden), ist nicht geprüft, weil kein Netz da ist.
3. **Tag-Bedingung.** Das Paket braucht je Auswahl eine Tag-Bedingung für den Eintrittsmarker. Alle 219 Elemente tragen `natural=cave_entrance`; das ist hier die Bedingung (`data/seeds/sisal.csv`, Vorschlag). Welche Elemente zur Menge gehören, bestimmt die ID-Liste, ab welcher Version sie „in der Auswahl“ sind, die Tag-Bedingung. Ein Element, das nie `natural=cave_entrance` hatte, würde als „nie in der Auswahl“ gemeldet.
4. **Herkunft der ID-Liste, nicht nachvollziehbar.** `py/SISAL/output/sisal_osm_matches.csv` hat 305 SISAL-Standorte, 170 mit Treffer (`has_match=True`), 135 ohne, und 159 verschiedene OSM-IDs; 11 Standorte teilen sich einen Node; die größte Entfernung ist 4,93 km (Suchradius 5 km). Die Liste mit den 221 IDs enthält nur 120 dieser 159 IDs; `output/osm_ids.json` und `output/osm_ids.txt` (159 Einträge) sind eine dritte Fassung. Die drei Dateien stammen aus verschiedenen Läufen der Zuordnung. Die Liste, die osm2lod tatsächlich abgefragt hat (221), ist die Grundlage hier; die Zuordnung SISAL-Standort → OSM-Node ist damit **nicht** reproduzierbar (Teil D).
5. **SISAL-Standorte.** `py/SISAL/sisal_sites_all.csv`: 305 Standorte (`site_id`, `site_name`, `wkt`, Zahl der δ18O- und δ13C-Proben). Der Datensatz selbst ist die SISAL-Datenbank (https://doi.org/10.17864/1947.408 laut README dort).
6. **Paket v0.24.1, Grenzen** (im Quelltext geprüft, `step_import_osm.py`): der Auswahlname ist `benchmarks`, solange `--selection` fehlt (hier setzt `main.py` `--selection sisal` selbst, siehe unten); die Beschreibungswörter sind fest („Benchmark“/„Höhenmarke“ als Rückfall), Höhlen würden als „Benchmark (OpenStreetMap node …)“ beschrieben (S3); `crm:E26` fehlt in der Klassentabelle des Pakets (nur ein Eintrag ohne Oberklasse).
7. **Umfang des Harvests.** 221 Anfragen nach 219 vorhandenen Elementen, mit 100 je Lauf mindestens 3 Läufe. Keine Ways, keine Stützpunkte. Overpass und die OSM-API sind aus der Sandbox dieses Chats nicht erreichbar (geprüft 2026-11-01); der Harvest läuft bei Flo.
8. **Skeleton ohne Daten** (geprüft 2026-11-01 mit `wikibase-static` v0.24.1): `python main.py --strict` läuft mit den Modelldateien (4 Klassen: Q1 bis Q3 und Q100; 24 Properties, 60 Statements) zweimal mit Exit-Code 0 durch; nach dem Einchecken von `data/derived/`, `dist/` und `docs/` ist `git status` leer, auch nach einem dritten Lauf. `check-crm` meldet 0 Verstöße, `check_attribution.py` findet „OpenStreetMap contributors“ in 63 Dateien. Anders als bei den Benchmarks in S1 (ohne Modell: „nothing to do“) erzeugt der Lauf also schon Seiten für die Modell-Entitäten. Ohne `queries.yaml` scheitert `--strict` an der Standardabfrage `coordinates` (keine Zeilen, WARN): `requires: [globe-coordinate]` prüft den Datentyp der Property P110, nicht ob es Statements gibt. Deshalb liegt eine vorläufige `queries.yaml` (Standardsatz ohne `coordinates`) im Repo, die mit dem ersten Harvest gelöscht wird.

---

### A2 Zielbild

```
 data/seeds/overpass-sisal.overpassql + data/seeds/sisal.csv     (221 Node-IDs aus osm2lod, Tag-Bedingung)
         │
         │ import-osm   (Verb mit Netz, nie im Standardlauf)
         ▼
 Overpass  ──►  data/raw/osm/overpass/<name>.json        Elemente und aktuelle Versionen
 OSM API   ──►  data/raw/osm/history/<type>_<id>.json   volle Historie (nur bei Versionsabweichung)
         │         data/raw/osm/members/                 Historien der Stützpunkte von Ways
         │ import-osm --offline  +  data/csv/mapping/osm-properties.csv
         ▼
 data/csv/  entities.csv  statements.csv  qualifiers.csv  references.csv  idmap.csv     data/crm.csv  (Cave → crm:E26)
         │ from-csv → load → build → search → rdf → sparql
         ▼
 docs/  (GitHub Pages: Seiten, Karte, Suche, SPARQL)      dist/*.ttl  (DCAT 3, GeoSPARQL, CIDOC CRM)
```

Eine QID je OSM-Element, die Versionen als Statements daran; das Beispiel mit den Statements und Qualifiern steht in A2 von `osm-benchmarks-static`.

Die Ergebnisse müssen diese Eigenschaften haben, jede ist prüfbar:

1. Jedes Element hat genau eine QID; es gibt keine Versions-Items.
2. Zahl der OSM-Version-Statements je Element = Zahl der Versionen in der API-History.
3. Jede QID ist über `data/crm.csv` auf eine CRM-Klasse verankert; `check-crm` meldet keinen Verstoß.
4. Das RDF enthält kein `owl:sameAs` auf OpenStreetMap; die Statement- und Wert-IRIs sind reine Bezeichner im eigenen Namensraum.
5. Zweimal laufen lassen ändert nichts (`git status` leer); ein zweiter Harvest ohne Änderung bei OSM stellt nur die Overpass-Anfrage.


### A3 Querschnittsregeln

- Rohdaten liegen unter `data/raw/`, unverändert wie erhalten, nicht von Hand ändern. Was ein Skript daraus macht, geht nach `data/csv/`, `data/derived/`, `dist/` oder `docs/`.
- Wiederverwendung heißt kopieren, nicht referenzieren. Das Modell (P100 bis P113) ist aus `osm-benchmarks-static` kopiert und bleibt dort wie hier gleich; Abweichungen stehen in A4.
- **Keine Uhr im Output.** Kein Generator ruft `datetime.now()` auf. Zeitangaben stammen aus den Quelldaten (Zeitstempel der OSM-Versionen) oder aus `RELEASE_DATE`.
- **Zeilenenden LF** (`.gitattributes`: `* text=auto eol=lf`).
- **Zweimal laufen lassen, `git status` bleibt sauber.**
- **Netzwerk nur im Verb `import-osm`.** Alles andere läuft offline gegen `data/raw/`; das Verb gehört nie zum Standardlauf.
- **Höflicher Harvest.** Ehrlicher User-Agent mit Kontaktadresse (`--contact`), mindestens eine Sekunde Pause zwischen Requests an die OSM API, `Retry-After` beachten, Overpass nur mit einer Abfrage zur Zeit; die OSM-Nutzungsregeln gelten.
- **Die Seiten zeigen, was die Quelle sagt.** Werte werden formatiert, nicht repariert.
- **Lizenz und Namensnennung.** Die Daten sind OpenStreetMap-Daten (ODbL 1.0, „© OpenStreetMap contributors“); der Hinweis steht auf jeder Seite und im RDF.
- Befehle für Windows `cmd`, jeder in **einer** Zeile, zusammengehörige Befehle mit `&&` verkettet.
- Mermaid-Diagramme nutzen das feste Farbschema der Familie (Subject/Object grau, RealObject dunkelgrün, Class dunkelorange, Term dunkelviolett, OWL weiß, PropMeta amber).

### A4 Beschlusslage

| Frage | Beschluss | seit |
|---|---|---|
| Zweck | Statische Wikibase (GitHub Pages) für die OSM-Elemente (Höhleneingänge), die zu SISAL-Standorten gehören; Weiterentwicklung von osm2lod wie bei den Benchmarks. Der Bezug zu den SISAL-Standorten ist ein eigener Schritt (S5) | 2026-11-01 |
| Repo-Zuschnitt | `sisal` als **eigenes** Repo; `holywells` und `ogham` in `osm-holywells-static` und `osm-ogham-static` | 2026-11-01 |
| Repo-Name und Ort | `n4o-rse/osm-sisal-static`, lokal `C:\git\osm-sisal-static` | Vorschlag 2026-11-01 |
| Klasse, ID | Q100 „Cave“ (de „Höhle“), `subclass of` Q3; Properties P100 bis P113 wie bei den Benchmarks; ein Eintrag der Rolle `class_benchmark` genügt (nur eine Klasse) | Vorschlag 2026-11-01 |
| CRM-Anker | `crm:E26` Physical Feature, wie osm2lod (`entityBaseClass`); `crm:E26` sollte für die Kette zu `crm:E18` einen Eintrag im Paket bekommen (S3) | Vorschlag 2026-11-01 |
| Auswahl | Name `sisal`; Menge = die 221 Node-IDs aus osm2lod (Befund 2); Tag-Bedingung für den Eintrittsmarker `natural=cave_entrance` (Befund 3) | Vorschlag 2026-11-01 |
| Auswahlname | `main.py` hängt bei `import-osm` `--selection sisal` an, wenn es fehlt (das Paket nimmt sonst `benchmarks`); die einzige Abweichung von `main.py` der Benchmarks | 2026-11-01 |
| Logo | Das Logo (`assets/logo.png`) ist die Zeichnung der Sinterwelt in der Kalksteinhöhle | Vorschlag 2026-11-01 |
| Modell | Wie `osm-benchmarks-static`, **1:1**: eine QID je OSM-Element, Versionen als Statements, Eintrittsmarker, Geometrie-Verlauf als WKT, Tags nur aktuell als `key=value`; Properties P100 bis P113 mit denselben IDs, Namen und Datentypen; Rolle → ID in `data/csv/mapping/osm-properties.csv`. Alle übrigen Beschlüsse der A4 dort (Identität, Versionen, Historie, Quelle, Austritt, Geometrie, Datentypen, Benutzername und uid, Label, URIs, Verb) gelten hier unverändert | 2026-11-01 |
| Seeds | Die Abfrage steht als Datei unter `data/seeds/overpass-<name>.overpassql`, aus osm2lod übernommen; geändert nur `out meta geom;` → `out meta;` (das Paket baut die Geometrie selbst) und das Zeitlimit 25 → 180 s (wie bei den Benchmarks). Die Tag-Bedingung steht als `data/seeds/<name>.csv` | 2026-11-01 |
| Lizenz | ODbL 1.0 mit „© OpenStreetMap contributors“ in `site.yaml` (`license`); der Code unter MIT; das Logo unter CC BY 4.0 (Vorschlag, siehe Teil D) | Vorschlag 2026-11-01 |
| URIs | Eigener Namensraum im github.io-Raum des Repos (`rdf_base`), eigene Präfixfamilie (`rdf_prefix`); kein `owl:sameAs` und kein `skos:exactMatch` auf OSM | Vorschlag 2026-11-01 |
| Skeleton | Wie `osm-benchmarks-static` (S1): dünnes `main.py` (setzt `WBS_ROOT`), `site.yaml`, `requirements.txt` auf `wikibase-static` v0.24.1, `update.cmd`, `check_attribution.py`, Workflow-Aufrufer mit `deploy: false`, bis die ersten Daten da sind | 2026-11-01 |
| Paket | Das Paket in v0.24.1 kann nur **eine** Klasse je Site, **eine** Auswahl je Lauf und fest eingebaute Beschreibungswörter (Befund 6); das Ändern ist Schritt S3 im Paket-Repo, nicht hier | 2026-11-01 |

### A5 Was in welchem Chat hochgeladen wird

Ein Bundle statt Einzeldateien. Mitnehmen: `PRIMER.md`, Quelltexte, kleine Daten (`data/raw/osm/`). Nicht mitnehmen: `.git/`, `.venv/`, `config.local.*`, große erzeugte Dateien.

```cmd
robocopy . ..\osm-sisal-static-bundle /E /XD .git .venv __pycache__ build /XF config.local.ini config.local.json >nul & powershell -NoProfile -Command "Compress-Archive -Path ..\osm-sisal-static-bundle\* -DestinationPath ..\osm-sisal-static-bundle.zip -Force"
```

(robocopy meldet Erfolg mit Exit-Code unter 8, das ist normal.) Das Paket `wikibase-static` und `osm-benchmarks-static` klont Claude selbst von GitHub. Ein Chat im Paket-Repo (S3) bekommt dessen PRIMER und dessen Bundle.

### A6 IRI-Landkarte

Alles `geplant`, bis die erste Veröffentlichung die Basis festlegt. Vorschlag: `rdf_base` = `https://n4o-rse.github.io/osm-sisal-static`, `rdf_prefix` = `oss`.

| Pfad | Inhalt | Ziel des Redirects | Status |
|---|---|---|---|
| `<base>/entity/<ID>` | Konzept-URI eines Elements (Weiterleitungsseite) | – | geplant |
| `docs/ttl/<ID>.ttl`, `docs/json/<ID>.json` | ein Element als Turtle bzw. JSON | – | geplant |
| `docs/downloads/<host>.ttl` | RDF aller Entitäten, beschrieben mit DCAT 3 | – | geplant |
| `docs/sparql.html`, `docs/query.html` | Query-Seite und Editor | – | geplant |
| w3id-Präfix | offen, wie im Paket vorerst keines | offen | geplant |

---

## Teil B — Schrittübersicht

| ID | Schritt | Repo | hängt ab von | Status |
|---|---|---|---|---|
| S0 | Festlegungen, Abfrage aus osm2lod, Befunde | osm-sisal-static | – | erledigt 2026-11-01 |
| S1 | Skeleton: Layout, `main.py`, `site.yaml`, `requirements.txt`, Lizenz, Citation, Workflow-Aufrufer, `update.cmd`, Logo | osm-sisal-static | S0 | gebaut 2026-11-01 (Patch-ZIP; Einspielen offen) |
| S2 | Modell: Klasse „Cave“, Properties P100 bis P113, `data/crm.csv`, Mapping-Datei, Seeds | osm-sisal-static | S1 | gebaut 2026-11-01 (Patch-ZIP; Einspielen offen) |
| S3 | Paket 0.25.0: Beschreibungswörter je Klasse statt der festen Tabelle, `crm:E26` in der Klassentabelle (gemeinsam für alle drei neuen Site-Repos) | wikibase-static | S2 | offen |
| S4 | Erstharvest: 221 Node-IDs, Overpass, Historien, Import, Seiten, RDF, `check-crm` | osm-sisal-static | S3 | offen |
| S5 | SISAL-Verknüpfung: Property „SISAL-Standort“ (ID, Name, Entfernung der Zuordnung) aus den Zuordnungsdateien; vorher klären, welche Zuordnung gilt (Befund 4) | osm-sisal-static | S4 | offen |
| S6 | Standardabfragen (`queries.yaml`): Versionen je Element, Eintrittsversion, SISAL-Standorte ohne und mit Höhle, Wikidata | osm-sisal-static | S5 | offen |
| S7 | Pages-Workflow scharf (`deploy` an, `check_attribution.py`), ODbL-Hinweis, CI mit `--strict` zweimal | osm-sisal-static | S4 | offen |

S1 und S2 sind in einem Patch. S3 gilt gleichzeitig für `osm-holywells-static` und `osm-ogham-static`: der Paket-Chat macht alles in einem Zug. S4 braucht S3 nur für die Beschreibungen und `crm:E26`; der Harvest selbst läuft mit dem Paket 0.24.1, nur mit falschen Beschreibungen (nicht committen). S5 hängt an der Klärung der Zuordnung, nicht an Technik.

---

## Teil C — Die Schritte

### S1 und S2 — Skeleton und Modell

**Ziel:** Ein Site-Repo nach dem Muster von `osm-benchmarks-static`, das mit `python main.py` ohne Daten sauber durchläuft und das Modell enthält.

**Uploads:** keine; Claude klont `osm-benchmarks-static` und osm2lod selbst.

Inhalt: Dateien wie bei den Benchmarks (S1 und S2 dort); neu sind die Klasse Q100 „Cave“ in `data/csv/entities.csv`, eine Zeile in `data/crm.csv`, `data/seeds/sisal.csv` und `data/seeds/overpass-sisal.overpassql` (221 Node-IDs). `main.py` setzt bei `import-osm` die Auswahl `sisal`. Der Workflow-Aufrufer hat `deploy: false` und prüft nur `python main.py --strict`; `check_attribution.py` ist da, läuft aber erst mit S7.

**Abnahme:** `python main.py --list` nennt die Schritte; `python main.py --strict` läuft ohne Daten durch; zwei Läufe hintereinander, `git status --porcelain` leer; `python main.py --strict check-crm` ohne Verstoß.

### Erledigt 2026-11-01 (S1, S2)

Gebaut: Dateien wie `osm-benchmarks-static` (`main.py`, `requirements.txt` auf v0.24.1, `site.yaml`, `LICENSE`, `CITATION.cff`, `update.cmd`, `check_attribution.py`, `.github/workflows/site.yml`, `README.md`), dazu das Modell (`data/csv/`, `data/crm.csv`, `data/csv/mapping/osm-properties.csv`), die Seeds (`data/seeds/`), das Logo und die vorläufige `queries.yaml` (Befund 7). Abnahme in einer frischen Kopie: `--list` nennt neun Einträge (sechs im Standardlauf, drei Verben), `--strict` zweimal und ein drittes Mal mit Exit-Code 0, `git status` leer, `check-crm` 0 Verstöße, `check_attribution.py` grün; `main.py` reicht `--selection` an `import-osm` weiter (mit einer Attrappe für den Aufruf geprüft, nicht mit Netz). Die Properties P100 bis P113 sind bis auf den Beispieltext in P107 und P109 gleich denen der Benchmarks (verglichen). Nicht geprüft: der Lauf des Workflows auf GitHub, `update.cmd` unter Windows, Overpass und OSM-API (kein Netz), die Seiten im Browser. Der Patch bringt kein `docs/`, `dist/` und `data/derived/` mit; sie entstehen beim ersten Lauf und werden mit eingecheckt.

### S3 — Paket 0.25.0

Der Auftrag an das Paket steht ausführlich im PRIMER von `osm-holywells-static` (S3). Für dieses Repo zählen davon zwei Punkte: die Beschreibungswörter je Klasse („Cave“/„Höhle“ statt „Benchmark“/„Höhenmarke“) und `crm:E26` in der Klassentabelle. **Abnahme:** ein Probe-Element (ein Höhleneingang) bekommt die Beschreibung „Cave entrance (OpenStreetMap node …)“ bzw. „Höhleneingang (OpenStreetMap-Node …)“ (Wortlaut im Paket-Chat festlegen); `check-crm` ohne Verstoß mit `crm:E26`.

### S4 — Erstharvest

**Ziel:** Die 221 Nodes sind importiert, die Seiten, das RDF und die SPARQL-Seite stehen.

**Uploads:** dieses Bundle (A5).

Inhalt: `python main.py import-osm --probe --contact <Adresse>` zuerst; dann `python main.py import-osm --contact <Adresse>` (drei Läufe wegen `--limit 100`), danach `python main.py --strict` zweimal. Elemente, die Overpass nicht liefert (Befund 2), bleiben ohne Item; ihre IDs werden im PRIMER notiert.

**Abnahme:** 219 Items (oder die Zahl der heutigen Overpass-Antwort), Zahl der Version-Statements je Element = Zahl der Versionen der API-History (Summe 649 am 2026-03-28, heute gleich oder höher), `check-crm` ohne Verstoß, zweiter Lauf ändert nichts.

### S5 bis S7

- **S5** Die SISAL-Verknüpfung braucht zuerst die Antwort auf die Frage in Teil D (welche Zuordnung gilt). Danach: eine Property „SISAL-Standort“ (ID, `external-id`; Formatter-URL offen) mit Qualifiern für den Namen des Standorts und die Entfernung in km, Quelle als Seed unter `data/seeds/`; Abnahme: jeder zugeordnete Standort steht an genau einem Item, ein Node mit mehreren Standorten (11 in `sisal_osm_matches.csv`) an mehreren Statements.
- **S6** Abfragen und **S7** Veröffentlichung wie bei `osm-benchmarks-static` (dort S7 und S8): `deploy: false` entfernen und `&& python check_attribution.py` im Aufrufer ergänzen.

---

## Teil D — Offene Punkte

- **Welche Zuordnung SISAL → OSM gilt (Befund 4):** Die Liste mit 221 IDs, `osm_ids.json` (159) und `sisal_osm_matches.csv` (159 verschiedene IDs, davon nur 120 in der Liste) stimmen nicht überein. Zu klären: aus welchem Lauf stammt die Liste, und soll die Zuordnung neu gerechnet werden (S5)? Bis dahin ist die Liste aus osm2lod die Menge dieser Site.
- **Repo-Name und Organisation:** `osm-sisal-static` unter `n4o-rse` ist ein Vorschlag. Alternativen: `osm-caves-static`, `sisal-osm-static`.
- **Logo:** Autor und Lizenz auch dieser Zeichnung klären (bei den Benchmarks: Florian Thiery, mit ChatGPT erzeugt, CC BY 4.0; das README nennt das hier ebenso, bis es bestätigt ist).
- **Klasse „Cave“:** Alle 219 Elemente sind `natural=cave_entrance`, also Höhleneingänge, nicht Höhlen. Das Etikett „Cave“ folgt dem Sprachgebrauch von osm2lod und SISAL; „Cave entrance“ wäre genauer. Zu entscheiden mit S3, weil die Beschreibung davon abhängt.
- **Zwei fehlende IDs (Befund 2):** 13581390702 und 13586189099 liefern im Lauf 2026-03-28 nichts. Beim Erstharvest prüfen (gelöscht? noch nicht sichtbar?), dann in A1 nachtragen.
- **Eintrittsregel:** `natural=cave_entrance` kann in einer frühen Version gefehlt haben; der Eintrittsmarker zeigt dann die spätere Version. Zu prüfen in S4.
- **Netz:** `import-osm` ist hier noch nicht gelaufen; beim ersten Lauf `--contact` setzen und die Pause prüfen.
