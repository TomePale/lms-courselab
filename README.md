<p align="center">
  <img src=".github/logo.svg" alt="CourseLab logo" width="112">
</p>

<h1 align="center">CourseLab</h1>

<p align="center">
  Platforma za tečajeve: objava, upisi i ograničen broj mjesta
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white" alt="Python 3.11+"></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI"></a>
  <a href="https://docs.pydantic.dev/"><img src="https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic&logoColor=white" alt="Pydantic v2"></a>
  <a href="https://www.sqlalchemy.org/"><img src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white" alt="SQLAlchemy 2.0"></a>
  <a href="https://alembic.sqlalchemy.org/"><img src="https://img.shields.io/badge/Alembic-migracije-6BA81E" alt="Alembic"></a>
  <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL 16"></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white" alt="Docker"></a>
  <br>
  <a href="https://docs.pytest.org/"><img src="https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white" alt="pytest"></a>
  <a href="https://docs.astral.sh/ruff/"><img src="https://img.shields.io/badge/code%20style-ruff-D7FF64?logo=ruff&logoColor=black" alt="Ruff"></a>
  <a href="https://github.com/TomePale/lms-courselab/commits/main"><img src="https://img.shields.io/github/last-commit/TomePale/lms-courselab" alt="Zadnji commit"></a>
</p>

Studentski projekt iz kolegija **Programiranje za web** na SIT UNIZD.

Platforma za tečajeve: treneri objavljuju tečajeve, studenti se upisuju, a
trener upis prihvaća ili odbija, uz ograničen broj mjesta. Administrator
upravlja korisnicima i smije sve što i trener, nad svim tečajevima.

Projekt ima dva dijela:

- **backend** (`api/`): REST API na FastAPI-ju i PostgreSQL-u, 1. dio projekta
- **frontend** (`web/`): Vue aplikacija, 2. dio projekta

## Tehnologije

| Područje | Alat |
| --- | --- |
| Jezik i okruženje | Python 3.11+, uv |
| Web okvir | FastAPI, Uvicorn |
| Validacija i postavke | Pydantic v2, pydantic-settings |
| Baza | PostgreSQL 16 u Dockeru, SQLAlchemy 2.0 (async), asyncpg |
| Migracije | Alembic |
| Sigurnost | bcrypt (hash lozinki), PyJWT (access i refresh token) |
| Testovi | pytest, pytest-asyncio, httpx, freezegun |
| Kvaliteta koda | ruff |

## Struktura

```
api/                     # backend: FastAPI
  app/
    main.py              # sastavljanje aplikacije, rute i handleri pogrešaka
    seed.py              # početni podaci (python -m app.seed)
    core/                # postavke, baza, sigurnost, JWT, ovisnosti, pogreške,
                         # sat (clock), izračun faze tečaja (phases), logging
    models/              # SQLAlchemy modeli: users, courses, enrollments,
                         # categories, reviews
    schemas/             # Pydantic sheme ulaza i izlaza
    repositories/        # upiti nad bazom
    services/            # poslovna pravila i provjere vlasništva
    routers/             # rute: primaju zahtjev, zovu servis, vraćaju odgovor
  alembic/versions/      # migracije baze 001 ... 007
  tests/                 # pytest
  requirements.txt       # zavisnosti
  pyproject.toml         # postavke za ruff i pytest
web/                     # frontend: Vue, dolazi u 2. dijelu
docker-compose.yml       # baza podataka
.env.example             # predložak konfiguracije
```

Ruta prima zahtjev i vraća odgovor, poslovno pravilo stoji u servisu, a upit
nad bazom samo u repozitoriju.

Uvicorn bilježi svaki zahtjev, a servisi uz to bilježe važne događaje
(stvoren i obrisan tečaj, prihvaćen i odbijen upis, obrisana kategorija,
nova recenzija), npr. `INFO app.services.course_service: course deleted: id=5`.

## Preduvjeti

- Git
- Python 3.11 ili noviji
- [uv](https://docs.astral.sh/uv/)
- Docker Desktop s alatom Docker Compose

## Pokretanje

```bash
# 1) Konfiguracija
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
# (ili python3); ispisani ključ upiši u .env umjesto promijeni-me

# 2) Baza
docker compose up -d db

# 3) Backend
cd api
uv venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
alembic upgrade head          # stvara tablice
python -m app.seed            # početni podaci (smije se pokrenuti više puta)
uvicorn app.main:app --reload
```

`JWT_SECRET_KEY` mora biti vlastiti nasumični ključ od barem 32 znaka. S
predloškom iz `.env.example` aplikacija se namjerno ne pokreće, jer bi njime
svatko mogao potpisati valjan token. Naredba iznad radi na svim sustavima,
a na macOS-u i Linuxu može i `openssl rand -hex 32`.

Provjera:

- http://127.0.0.1:8000/health vraća `{"status": "ok"}`
- http://127.0.0.1:8000/docs prikazuje Swagger UI s popisom ruta

## Testni računi

`python -m app.seed` stvara ove račune:

| Uloga | Email | Lozinka |
| --- | --- | --- |
| admin | `admin@courselab.hr` | `admin123` |
| trainer | `trener@courselab.hr` | `trener123` |
| student | `student1@courselab.hr` | `student123` |
| student | `student2@courselab.hr` | `student123` |
| student | `student3@courselab.hr` | `student123` |
| student | `student4@courselab.hr` | `student123` |

Uz to stvara kategorije *Programiranje* i *Baze podataka* i tri tečaja
trenera `trener@courselab.hr`, s datumima računatima od trenutka prvog
pokretanja:

| Tečaj | Kategorija | Faza | Kapacitet | Upisi |
| --- | --- | --- | --- | --- |
| *Uvod u Python* | Programiranje | upisi otvoreni | 3 | `student4` prihvaćen; `student2` i `student3` čekaju odluku |
| *Baze podataka* | Baze podataka | u tijeku | 10 | `student1` i `student3` prihvaćeni |
| *Git osnove* | Programiranje | završen | 10 | `student1` prihvaćen i napisao recenziju (ocjena 5) |

Seed je idempotentan: svaki zapis traži se po svom jedinstvenom ključu
(email, naziv kategorije, trener i naziv tečaja, student i tečaj) i stvara
samo ako ne postoji, pa drugo pokretanje ne stvara duplikate.

## Baza i migracije

Pet tablica: `users`, `categories`, `courses`, `enrollments` i `reviews`.
Trener ima više tečajeva (1:N), kategorija ima više tečajeva (1:N), a
student i tečaj povezani su upisima (N:M preko `enrollments`) i
recenzijama (`reviews`).

| Rev | Promjena |
| --- | --- |
| 001 | tablica `users`, ENUM `user_role`, UNIQUE na emailu |
| 002 | stupac `users.is_active` (NOT NULL, `server_default true`) |
| 003 | tablica `courses`, ENUM `course_status`, FK na trenera, CHECK `capacity > 0` |
| 004 | CHECK poretka datuma tečaja i UNIQUE (`trainer_id`, `title`) |
| 005 | tablica `enrollments`, ENUM `enrollment_status`, oba FK, UNIQUE (`student_id`, `course_id`), indeks (`course_id`, `status`) |
| 006 | tablica `categories` (UNIQUE na nazivu) i stupac `courses.category_id` (FK, nullable, indeks) |
| 007 | tablica `reviews`, oba FK, UNIQUE (`course_id`, `student_id`), CHECK ocjene 1–5 |

Shema baze mijenja se isključivo migracijama u `api/alembic/versions/`.
Naredbe se pokreću iz mape `api/`:

```bash
alembic revision --autogenerate --rev-id 008 -m "opis promjene"   # nova migracija
alembic upgrade head      # primijeni sve migracije
alembic downgrade -1      # poništi zadnju
alembic current           # na kojoj je migraciji baza
```

Svaka nova migracija čita se prije pokretanja i provjerava s
`upgrade head` → `downgrade -1` → `upgrade head`. Autogenerate ne briše
PostgreSQL ENUM tipove u `downgrade()` i ne prepoznaje CHECK ograničenja na
postojećoj tablici, pa se to dopisuje ručno.

Prazna baza:

```bash
docker compose down -v        # briše kontejner i podatke
docker compose up -d db
cd api && alembic upgrade head && python -m app.seed
```

## Testovi

```bash
cd api
pytest
```

36 testova pokriva prijavu, tokene i promjenu lozinke, uloge, vlasništvo i poslovna pravila
(rok upisa, kapacitet, prijelazi statusa, brisanje tečaja i kategorije,
recenzije). Pravila koja
ovise o vremenu testiraju se sa zamrznutim vremenom (freezegun), na
granicama: sekundu prije i sekundu poslije roka upisa te točno na granici
svake faze tečaja.

Korisne varijante (iz mape `api/`, s aktiviranim `.venv`):

| Naredba | Što radi |
| --- | --- |
| `pytest -q` | kratak ispis: točkica po testu i zbroj na kraju |
| `pytest -v` | svaki test u svom retku, s `PASSED` ili `FAILED` |
| `pytest tests/test_auth.py -v` | samo testovi iz jedne datoteke |
| `pytest tests/test_auth.py::test_login_success -v` | samo jedan test (ime iza `::`) |
| `pytest -k expired -v` | samo testovi čije ime sadrži zadanu riječ |
| `pytest -x` | stane na prvom testu koji padne |
| `pytest --lf -v` | ponovno pokreće samo testove koji su pali prošli put |
| `pytest -s` | prikazuje i `print()` iz testova |

Kad test padne, pytest ispiše redak u kojem je pao i vrijednosti koje je
uspoređivao (npr. `assert 403 == 401`).

Testovi rade nad zasebnom bazom `courselab_test` (varijabla
`TEST_DATABASE_URL`) na istom poslužitelju; stvara se sama pri prvom
pokretanju. Shema se stvara migracijama, a tablice se prazne prije svakog
testa.

## Kvaliteta koda

```bash
cd api
ruff format .     # jedinstven stil
ruff check .      # pogreške vidljive iz koda
```

## API

Access token šalje se u zaglavlju `Authorization: Bearer <token>` i traje 15
minuta; refresh token traje 7 dana. Popisi primaju `limit` (zadano 20, najviše
100) i `offset` (zadano 0) i vraćaju
`{"items": [...], "total": N, "limit": 20, "offset": 0}`.

### Općenito

| Metoda | Putanja | Opis | Pristup |
| --- | --- | --- | --- |
| GET | `/health` | provjera rada | javno |

### Autentikacija (`/auth`)

| Metoda | Putanja | Opis | Pristup |
| --- | --- | --- | --- |
| POST | `/auth/login` | prijava, vraća access i refresh token | javno |
| POST | `/auth/refresh` | novi par tokena | refresh token |
| GET | `/auth/me` | trenutni korisnik | prijavljen |
| POST | `/auth/change-password` | promjena vlastite lozinke uz trenutnu lozinku (204) | prijavljen |

### Korisnici (`/users`)

| Metoda | Putanja | Opis | Pristup |
| --- | --- | --- | --- |
| GET | `/users/` | popis korisnika, filtar `role` | admin |
| POST | `/users/` | novi korisnik | admin |
| GET | `/users/{id}` | jedan korisnik | admin |
| PATCH | `/users/{id}` | ime, prezime, uloga, `is_active` | admin |
| POST | `/users/{id}/reset-password` | nova lozinka (204) | admin |

### Kategorije (`/categories`)

| Metoda | Putanja | Opis | Pristup |
| --- | --- | --- | --- |
| GET | `/categories/` | popis kategorija | prijavljen |
| POST | `/categories/` | nova kategorija | admin |
| PATCH | `/categories/{id}` | promjena naziva | admin |
| DELETE | `/categories/{id}` | brisanje kategorije bez tečajeva (204) | admin |

### Tečajevi (`/courses`)

| Metoda | Putanja | Opis | Pristup |
| --- | --- | --- | --- |
| GET | `/courses/` | popis tečajeva s izračunatom fazom | admin: svi; trener: svoji i objavljeni; student: objavljeni |
| POST | `/courses/` | novi tečaj (`draft`), opcionalno `category_id`; vlasnik je onaj tko ga stvori | trener, admin |
| GET | `/courses/{id}` | jedan tečaj | kao popis |
| PATCH | `/courses/{id}` | naziv, opis, kapacitet, `category_id` (`null` miče kategoriju) | vlasnik, admin |
| POST | `/courses/{id}/publish` | `draft` → `published` | vlasnik, admin |
| POST | `/courses/{id}/archive` | `published` → `archived` | vlasnik, admin |
| DELETE | `/courses/{id}` | brisanje tečaja bez upisa (204) | vlasnik, admin |

### Upisi (`/enrollments`)

| Metoda | Putanja | Opis | Pristup |
| --- | --- | --- | --- |
| POST | `/courses/{id}/enrollments/` | upis na tečaj | student |
| GET | `/courses/{id}/enrollments/` | upisi tečaja | vlasnik, admin |
| GET | `/me/enrollments/` | moji upisi | student |
| GET | `/enrollments/{id}` | jedan upis | student vlasnik upisa, vlasnik tečaja, admin |
| POST | `/enrollments/{id}/accept` | prihvaćanje upisa (kapacitet) | vlasnik tečaja, admin |
| POST | `/enrollments/{id}/reject` | odbijanje upisa | vlasnik tečaja, admin |

### Recenzije (`/reviews`)

| Metoda | Putanja | Opis | Pristup |
| --- | --- | --- | --- |
| POST | `/courses/{id}/reviews/` | recenzija završenog tečaja | prihvaćeni student |
| GET | `/courses/{id}/reviews/` | recenzije tečaja | tko vidi tečaj |

Admin smije sve što i vlasnik tečaja, nad svim tečajevima. Status tečaja i
upisa ne mijenja se PATCH-om, nego zasebnim radnjama (`publish`, `archive`,
`accept`, `reject`), jer svaka ima svoje pravilo.

## Tko što smije

"Vlasnik" je trener koji je stvorio tečaj, a "tuđi trener" svaki drugi
trener. Uloga se provjerava ovisnošću `require_role`, a vlasništvo u servisu
(`can_manage`).

| Radnja | Admin | Trener vlasnik | Tuđi trener | Student | Neprijavljen |
| --- | :-: | :-: | :-: | :-: | :-: |
| prijava, obnova tokena | ✓ | ✓ | ✓ | ✓ | ✓ |
| vlastiti podaci (`/auth/me`) | ✓ | ✓ | ✓ | ✓ | ✗ |
| promjena vlastite lozinke | ✓ | ✓ | ✓ | ✓ | ✗ |
| upravljanje korisnicima (`/users/`) | ✓ | ✗ | ✗ | ✗ | ✗ |
| stvaranje tečaja | ✓ | ✓ | ✓ | ✗ | ✗ |
| pregled objavljenih tečajeva | ✓ | ✓ | ✓ | ✓ | ✗ |
| pregled nacrta (`draft`) | ✓ | ✓ | ✗ (404) | ✗ (404) | ✗ |
| izmjena tečaja (naziv, opis, kapacitet) | ✓ | ✓ | ✗ | ✗ | ✗ |
| objava i arhiviranje tečaja | ✓ | ✓ | ✗ | ✗ | ✗ |
| brisanje tečaja (samo bez upisa) | ✓ | ✓ | ✗ | ✗ | ✗ |
| upis na tečaj | ✗ | ✗ | ✗ | ✓ | ✗ |
| pregled svojih upisa (`/me/enrollments/`) | ✗ | ✗ | ✗ | ✓ | ✗ |
| pregled upisa tečaja | ✓ | ✓ | ✗ | ✗ | ✗ |
| pregled jednog upisa | ✓ | ✓ | ✗ | samo svoj | ✗ |
| prihvaćanje i odbijanje upisa | ✓ | ✓ | ✗ | ✗ | ✗ |
| pregled kategorija | ✓ | ✓ | ✓ | ✓ | ✗ |
| upravljanje kategorijama | ✓ | ✗ | ✗ | ✗ | ✗ |
| pisanje recenzije (prihvaćen, tečaj završen) | ✗ | ✗ | ✗ | ✓ | ✗ |
| pregled recenzija tečaja | ✓ | ✓ | ako vidi tečaj | ako vidi tečaj | ✗ |

Zabranjena radnja vraća 403 `forbidden`, a neprijavljen korisnik 401. Tuđi
nacrt vraća 404, pa se iz odgovora ne vidi ni da tečaj postoji.

## Faze tečaja

Faza se ne sprema nego se računa pri svakom zahtjevu iz datuma tečaja i
trenutnog vremena (`app/core/phases.py`), pa nikad ne zastarijeva.

| Faza | Traje |
| --- | --- |
| `enrollment_open` | `now < enrollment_deadline` |
| `enrollment_closed` | `enrollment_deadline <= now < start_date` |
| `in_progress` | `start_date <= now < end_date` |
| `finished` | `now >= end_date` |

Upis je moguć samo u fazi `enrollment_open` i samo na tečaj u statusu
`published`. Recenzija je moguća samo u fazi `finished`. Prihvaćanje i
odbijanje upisa ne ovise o fazi.

## Poslovna pravila

| Pravilo | Pogreška |
| --- | --- |
| upis samo do roka za upis | 400 `enrollment_closed` |
| upis samo na objavljen tečaj | 400 `course_not_published` |
| jedan upis po studentu na tečaj | 409 `duplicate` |
| prihvaćanje samo dok ima mjesta (redak tečaja zaključan s `SELECT ... FOR UPDATE`) | 409 `course_full` |
| tečaj: `draft` → `published` → `archived`; upis: `pending` → `accepted` / `rejected` | 400 `invalid_status_transition` |
| datumi tečaja: `enrollment_deadline <= start_date < end_date` (i CHECK u bazi) | 400 `invalid_dates` |
| tečaj s upisima ne briše se nego arhivira | 409 `course_has_enrollments` |
| kategorija koju koriste tečajevi ne briše se | 409 `category_has_courses` |
| recenziju piše samo student s prihvaćenim upisom | 403 `not_enrolled` |
| recenzija tek kad je tečaj završen | 400 `course_not_finished` |
| jedna recenzija po studentu na tečaj | 409 `duplicate` |
| tuđi tečaj ili upis | 403 `forbidden` ili 404 `not_found` |

## Pogreške

Svaka pogreška vraća tijelo istog oblika:

```json
{ "code": "course_full", "message": "Tečaj je popunjen." }
```

`code` je stalan i namijenjen klijentu, `message` čovjeku. Pogreška 422 uz
to nosi polje `errors` s popisom polja koja nisu prošla provjeru:
`[{"field": "password", "message": "..."}]`.

| `code` | HTTP | Kada |
| --- | --- | --- |
| `validation_error` | 422 | tijelo ili parametri ne odgovaraju shemi; nepostojeća kategorija tečaja |
| `invalid_credentials` | 401 | kriva lozinka, nepostojeći ili deaktiviran korisnik, neispravan token |
| `token_expired` | 401 | token je istekao |
| `wrong_password` | 400 | trenutna lozinka kod promjene lozinke nije ispravna |
| `forbidden` | 403 | uloga ili vlasništvo ne dopuštaju radnju |
| `not_found` | 404 | zapis ne postoji ili ga korisnik ne smije vidjeti |
| `duplicate` | 409 | zapis bi prekršio jedinstvenost |
| `integrity_error` | 409 | podaci krše drugo ograničenje baze |
| `course_full` | 409 | tečaj je popunjen |
| `course_has_enrollments` | 409 | tečaj ima upise, pa se ne briše nego arhivira |
| `invalid_status_transition` | 400 | prijelaz statusa nije dopušten |
| `invalid_dates` | 400 | datumi tečaja nisu u ispravnom poretku |
| `course_not_published` | 400 | tečaj nije objavljen |
| `enrollment_closed` | 400 | rok za upis je prošao |
| `category_has_courses` | 409 | kategoriju koriste tečajevi, pa se ne briše |
| `not_enrolled` | 403 | student nema prihvaćen upis na tečaj |
| `course_not_finished` | 400 | tečaj još nije završio |

## Stanje projekta

Backend se gradi u 8 faza. Gotovo:

- [x] **Faza 0: postavljanje**: repozitorij, PostgreSQL u Dockeru, postavke
  iz `.env` (pydantic-settings), FastAPI aplikacija s `GET /health`, ruff
- [x] **Faza 1: baza i infrastruktura**: asinkrona veza s bazom (SQLAlchemy
  2.0, asyncpg), Alembic, tablica `users` (migracija 001), jedinstveni format
  pogrešaka, pytest nad zasebnom testnom bazom
- [x] **Faza 2: autentikacija**: hash lozinki (bcrypt), access i refresh
  JWT tokeni, `POST /auth/login`, `POST /auth/refresh`, `GET /auth/me`, seed
  s administratorom (`python -m app.seed`), testovi prijave i tokena
- [x] **Faza 3: korisnici i uloge**: deaktivacija korisnika (`is_active`,
  migracija 002), provjera uloga (`require_role`), straničenje popisa
  (`limit`, `offset`, `total`), rute `/users/` za administratora (popis,
  stvaranje, čitanje, izmjena, reset lozinke), testovi ovlasti
- [x] **Faza 4: tečajevi**: tablica `courses` (migracije 003 i 004), faza
  tečaja računa se iz datuma (`compute_phase`), vlasnik je onaj tko stvori
  tečaj, a admin smije sve; objava, arhiviranje i brisanje tečaja, testovi
  vlasništva i faza uz zamrznuto vrijeme (freezegun)
- [x] **Faza 5: upisi**: tablica `enrollments` (migracija 005), upis do roka,
  prihvaćanje i odbijanje uz provjeru kapaciteta (`SELECT ... FOR UPDATE`),
  zabrana brisanja tečaja s upisima, testovi pravila upisa
- [x] **Faza 6: početni podaci i dorada**: seed s trenerom, četiri studenta,
  dva tečaja u različitim fazama i upisima, potpuni README
- [x] **Faza 7: kategorije, recenzije i logging**: tablica `categories`
  (migracija 006) i kategorija tečaja, tablica `reviews` (migracija 007):
  recenziju piše prihvaćeni student nakon završetka tečaja, jednom po tečaju;
  logging važnih događaja u servisima

## Commitovi

Poruke prate oblik `vrsta(dio): namjera`; pravila su u
[`.github/commit-guidelines.md`](.github/commit-guidelines.md).
