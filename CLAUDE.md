# OCO — Istruzioni per Claude Code

Questo file contiene le istruzioni operative per lo sviluppo di OCO con Claude Code.
La documentazione di analisi completa si trova nei file `0x_*.md` nella stessa directory.

---

## Documenti di Riferimento

| File | Contenuto |
|---|---|
| `01_ANALYSIS.md` | Analisi generale, stack, workflow, architettura |
| `02_DATA_MODEL.md` | Schema DB completo, note SQLite/PostgreSQL |
| `03_TASKS.md` | **Piano di sviluppo — leggere prima di ogni task** |
| `04_API_CONTRACT.md` | Contratto API REST completo |
| `05_AI_ASYNC_QUEUE.md` | Architettura coda AI asincrona, stati item |

**Prima di iniziare qualsiasi task**, leggere il documento `03_TASKS.md` per identificare le checklist e la Definition of Done del task corrente.

---

## Struttura del Progetto

```
oco/                        ← questa directory (root progetto)
├── CLAUDE.md               ← questo file
├── 01_ANALYSIS.md
├── 02_DATA_MODEL.md
├── 03_TASKS.md
├── 04_API_CONTRACT.md
├── 05_AI_ASYNC_QUEUE.md
├── .venv/                  ← virtual environment Python (già esistente)
├── backend/
│   ├── app/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   └── vite.config.ts
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env
├── .env.example
└── Makefile
```

---

## Ambiente Python

Il virtual environment è in `.venv/` nella root del progetto (stessa directory di questo file).

```bash
# Attivare il venv
source .venv/bin/activate

# Installare dipendenze backend
pip install -r backend/requirements.txt

# Non creare altri venv — usare sempre quello esistente in .venv/
```

---

## Comandi di Sviluppo

### Backend (Python / FastAPI)

```bash
# Tutti i comandi vanno eseguiti con il venv attivo

# Avviare il backend in development
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Eseguire le migrazioni
alembic upgrade head

# Creare una nuova migrazione
alembic revision --autogenerate -m "descrizione"

# Eseguire i test backend
pytest

# Test con coverage
pytest --cov=app --cov-report=term-missing

# Test specifico
pytest tests/test_auth.py -v

# Test con output dettagliato su fallimento
pytest -v --tb=short
```

### Frontend (Vue 3 / Vite)

```bash
cd frontend

# Installare dipendenze
npm install

# Dev server (con proxy → backend su :8000)
npm run dev

# Build produzione
npm run build

# Eseguire test unitari
npm run test

# Test con watch
npm run test:watch

# Test E2E Playwright
npm run test:e2e

# Type check
npm run type-check

# Lint
npm run lint
```

### Docker / Podman

```bash
# Avviare tutto (usa podman-compose se disponibile, altrimenti docker-compose)
podman-compose up -d
# oppure
docker-compose up -d

# Rebuild dopo modifiche a Dockerfile o requirements
podman-compose up -d --build backend

# Log in tempo reale
podman-compose logs -f backend
podman-compose logs -f frontend

# Shell nel container backend
podman-compose exec backend bash

# Stop
podman-compose down

# Stop e rimuovi volumi (reset completo DB)
podman-compose down -v
```

### Makefile

```bash
make up          # podman-compose up -d
make down        # podman-compose down
make logs        # logs -f tutti i servizi
make build       # rebuild immagini
make test-be     # pytest nel venv locale
make test-fe     # vitest
make test-e2e    # playwright
make migrate     # alembic upgrade head
make shell-be    # shell nel container backend
make init-db     # crea schema + utente admin iniziale
```

---

## Workflow per Ogni Task

1. **Leggi** la sezione del task corrente in `03_TASKS.md`
2. **Implementa** tutti i punti della checklist
3. **Scrivi i test** prima o insieme all'implementazione (non dopo)
4. **Esegui i test**: `pytest` per backend, `npm run test` per frontend
5. **Esegui i test E2E** se previsti dal task (dal Task 05 in poi)
6. **Aggiorna il README.md** e la documentazione se il task impatta installazione/configurazione
7. **Verifica la Definition of Done** del task prima di dichiararlo completato
8. Comunica all'utente il completamento con un riepilogo di cosa è stato fatto e i risultati dei test

---

## Regole di Sviluppo

### Generali

- **Mai secrets nel codice** — tutto da variabili d'ambiente (`.env`), mai hardcoded
- **Mai rompere la compatibilità API** tra task — le modifiche agli endpoint esistenti devono essere backward compatible
- **`.env.example`** va aggiornato ogni volta che si aggiunge una nuova variabile d'ambiente, con commento esplicativo
- **Nessun `print()` di debug** lasciato nel codice — usare il logger configurato
- Usare **type hints** ovunque nel codice Python
- Usare **TypeScript strict** nel frontend, niente `any` impliciti

### Database e Migrazioni

- Le migrazioni Alembic sono **immutabili** una volta create — nuove modifiche = nuova migrazione, mai modificare una migrazione esistente
- Ogni migrazione deve essere **reversibile** (implementare `downgrade()`)
- Testare sempre la migrazione sia su SQLite che su PostgreSQL (se disponibile)
- Usare **UUID v4** per tutti gli ID primari

### Backend FastAPI

- Ogni router sta in `app/api/{dominio}.py`
- La business logic sta in `app/services/{dominio}_service.py` — i router sono thin, delegano al service
- Le dipendenze FastAPI (`Depends(...)`) stanno in `app/core/deps.py`
- Tutti gli endpoint richiedono autenticazione salvo `/api/auth/login`
- Gli errori usano il formato `{"detail": "messaggio", "code": "ERROR_CODE"}`
- Usare **Pydantic v2** per tutti gli schema (request/response)
- I modelli SQLAlchemy stanno in `app/models/`, gli schema Pydantic in `app/schemas/`

### Frontend Vue

- Usare **Composition API** con `<script setup>` — mai Options API
- Ogni store Pinia in `src/stores/{dominio}.ts`
- Le chiamate API passano tutte per `src/services/api.ts` (istanza Axios centralizzata)
- I componenti riutilizzabili stanno in `src/components/`
- Le view (pagine intere) stanno in `src/views/`
- **Niente testo hardcoded** nelle template — tutto passa per `vue-i18n` (`$t('chiave')`)
- Le chiavi i18n seguono la convenzione `dominio.componente.elemento` (es. `container.card.status.open`)

### AI e Worker

- I test che coinvolgono l'AI usano **sempre mock/fixture** — mai chiamare provider reali nei test automatici
- Il worker asincrono non deve mai crashare il processo FastAPI — tutti gli errori sono catturati e loggati
- Il timeout AI è configurabile via `AI_TIMEOUT_SECONDS` (default 60)
- Il modello Ollama di default è `llava-llama3` — documentarlo sempre nel README

### File e Storage

- Le foto vengono compresse lato client (max 1920px, JPEG 85%) prima dell'upload
- Il percorso storage è configurabile via `STORAGE_PATH` env var
- Struttura path: `{STORAGE_PATH}/{house_id}/{entity_type}/{entity_id}/{uuid}.jpg`
- I file temporanei (temp-photos AI) vengono eliminati dopo 1 ora se non associati

### Docker / Podman

- I Dockerfile usano **utente non-root**
- Compatibili con sia `docker-compose` che `podman-compose` (nessuna feature Docker-only)
- Le istruzioni nel README usano `podman-compose` come comando principale con nota su Docker come alternativa

---

## Variabili d'Ambiente

Documentate in `.env.example`. Le principali:

```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./data/oco.db
# Per PostgreSQL: postgresql+asyncpg://user:pass@host/dbname

# Sicurezza
SECRET_KEY=cambia-questa-chiave-in-produzione
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

# Admin iniziale (usato solo da init_db.py al primo avvio)
INITIAL_ADMIN_USERNAME=admin
INITIAL_ADMIN_EMAIL=admin@example.com
INITIAL_ADMIN_PASSWORD=cambia-questa-password

# Storage
STORAGE_PATH=./data/media

# AI
AI_PROVIDER=ollama              # ollama | claude | mistral
AI_TIMEOUT_SECONDS=60

# Ollama
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=llava-llama3

# Claude API (opzionale)
CLAUDE_API_KEY=

# Mistral API (opzionale)
MISTRAL_API_KEY=

# App
APP_HOST=http://localhost:3000  # usato per generare URL nei QR code
LOG_LEVEL=INFO
```

---

## Test

### Convenzioni Backend

- I test stanno in `backend/tests/`
- Struttura speculare al codice: `tests/api/test_auth.py`, `tests/services/test_item_service.py`, ecc.
- Usare `pytest-asyncio` per test asincroni
- Il DB di test è **SQLite in-memory** — nessun file su disco
- I fixture comuni stanno in `tests/conftest.py`
- I mock AI stanno in `tests/fixtures/ai_mocks.py`

```python
# Esempio fixture minima
@pytest.fixture
async def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

### Convenzioni Frontend

- I test unitari Vitest stanno in `src/**/__tests__/` o con suffisso `.test.ts`
- I test E2E Playwright stanno in `frontend/e2e/`
- Usare `@vue/test-utils` per montare componenti
- Le API sono sempre mockate nei test unitari

### Coverage Target

- Backend: **> 80%** di coverage complessiva
- I path critici (auth, item create/confirm, worker AI) devono avere **coverage 100%**

---

## Comunicazione con l'Utente

Al completamento di ogni task, fornire un riepilogo strutturato:

```
## Task XX completato

### Cosa è stato implementato
- [lista delle feature implementate]

### Test
- pytest: XX passed, 0 failed (coverage: XX%)
- vitest: XX passed, 0 failed
- E2E: XX scenari passati (se applicabile)

### Note
- [eventuali deviazioni dall'analisi, decisioni prese, problemi incontrati]

### Prossimo task
- Task XX — [titolo] è il prossimo step
```

Se durante lo sviluppo emergono ambiguità o decisioni architetturali non coperte dai documenti di analisi, **fermarsi e chiedere** prima di procedere con un'assunzione.
