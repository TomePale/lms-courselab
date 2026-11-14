# CourseLab

Studentski projekt iz kolegija **Programiranje za web** na SIT UNIZD.

Pojednostavljena platforma za učenje: treneri objavljuju tečajeve i zadaće,
studenti se upisuju i predaju rješenja, a administrator upravlja korisnicima i
vidi sve zapise.

Projekt ima dva dijela:

- **backend** (`api/`): REST API na FastAPI-ju i PostgreSQL-u, 1. dio projekta
- **frontend** (`web/`): Vue aplikacija, 2. dio projekta

## Stanje projekta

Backend se gradi u 8 faza. Gotovo:

- [x] **Faza 0: postavljanje**: repozitorij, PostgreSQL u Dockeru, postavke
  iz `.env` (pydantic-settings), FastAPI aplikacija s `GET /health`, ruff
- [x] **Faza 1: baza i infrastruktura**: asinkrona veza s bazom (SQLAlchemy
  2.0, asyncpg), Alembic, tablica `users` (migracija 001), jedinstveni format
  pogrešaka, pytest nad zasebnom testnom bazom
- [ ] Faza 2: autentikacija (bcrypt, JWT, `/auth/login`, `/auth/refresh`, `/auth/me`)
- [ ] Faza 3: korisnici i uloge
- [ ] Faza 4: tečajevi i faze tečaja
- [ ] Faza 5: upisi i kapacitet
- [ ] Faza 6: zadaće, predaje i ocjene
- [ ] Faza 7: završetak tečaja i dorada

## Tehnologije

| Područje | Alat |
| --- | --- |
| Jezik i okruženje | Python 3.11+, uv |
| Web okvir | FastAPI, Uvicorn |
| Validacija i postavke | Pydantic v2, pydantic-settings |
| Baza | PostgreSQL 16 u Dockeru, SQLAlchemy 2.0 (async), asyncpg |
| Migracije | Alembic |
| Testovi | pytest, pytest-asyncio, httpx |
| Kvaliteta koda | ruff |

## Struktura

```
api/                     # backend: FastAPI
  app/
    main.py              # sastavljanje aplikacije, rute i handleri pogrešaka
    core/                # postavke, veza s bazom, ovisnosti, pogreške
    models/              # SQLAlchemy modeli, jedan modul po tablici
    schemas/             # Pydantic sheme ulaza i izlaza
    repositories/        # upiti nad bazom
    services/            # poslovna pravila
    routers/             # rute: primaju zahtjev, zovu servis, vraćaju odgovor
  alembic/versions/      # migracije baze (001, 002, ...)
  tests/                 # pytest
  requirements.txt       # zavisnosti
  pyproject.toml         # postavke za ruff i pytest
web/                     # frontend: Vue, dolazi u 2. dijelu
docker-compose.yml       # baza podataka
.env.example             # predložak konfiguracije
```

## Preduvjeti

- Git
- Python 3.11 ili noviji
- [uv](https://docs.astral.sh/uv/)
- Docker Desktop s alatom Docker Compose

## Pokretanje

```bash
# 1) Konfiguracija
cp .env.example .env

# 2) Baza
docker compose up -d db

# 3) Backend
cd api
uv venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
alembic upgrade head          # stvara tablice
uvicorn app.main:app --reload
```

Provjera:

- http://127.0.0.1:8000/health vraća `{"status": "ok"}`
- http://127.0.0.1:8000/docs prikazuje Swagger UI s popisom ruta

## Baza i migracije

Shema baze mijenja se isključivo migracijama u `api/alembic/versions/`.
Naredbe se pokreću iz mape `api/`:

```bash
alembic revision --autogenerate --rev-id 002 -m "opis promjene"   # nova migracija
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
cd api && alembic upgrade head
```

## Testovi

```bash
cd api
pytest
```

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

## Pogreške

Svaka pogreška vraća tijelo istog oblika:

```json
{ "code": "not_found", "message": "Not Found" }
```

`code` je stalan i namijenjen klijentu, `message` čovjeku. Pogreška 422 uz
to nosi polje `errors` s popisom polja koja nisu prošla provjeru.

## Commitovi

Poruke prate oblik `vrsta(dio): namjera`; pravila su u
[`.github/commit-guidelines.md`](.github/commit-guidelines.md).
