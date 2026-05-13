# Win-Auto — AI-Powered Windows Desktop Automation

Describe what you want to automate in plain English, and Win-Auto generates a structured PyWinAuto script, lets you review it, runs it on your Windows desktop, and iterates until it works. Save working automations to a library and re-run them anytime.

**Example:** "Open SQL Server Management Studio, run a query on SalesDB, copy the results to Excel, create a chart, and email it via Outlook."

## Prerequisites

- **Windows 10/11** (PyWinAuto requires Windows)
- **Python 3.10+** with pip
- **Node.js 18+** with Yarn (for frontend development)
- **Anthropic API key** ([console.anthropic.com](https://console.anthropic.com))

## Quick Start (Development)

### Option A: Single Command (Recommended)

```bash
cd win-auto
npm install              # installs concurrently
npm run install:all      # installs frontend dependencies
cd backend && pip install -r requirements.txt && cd ..
copy .env.example backend/.env   # Windows
# cp .env.example backend/.env   # macOS/Linux
```

Edit `backend/.env` and add your API key:

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Start both servers:

```bash
npm run dev
```

This launches the backend (port 8000) and frontend (port 5173) together. Open `http://localhost:5173`.

### Option B: Manual (Separate Terminals)

**Terminal 1 — Backend:**

```bash
cd win-auto/backend
pip install -r requirements.txt
copy .env.example .env
python main.py
```

The backend runs at `http://localhost:8000`. Verify with `curl http://localhost:8000/health`.

**Terminal 2 — Frontend:**

```bash
cd win-auto/frontend
yarn install
yarn dev
```

Open `http://localhost:5173` in your browser.

### Available npm Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start backend + frontend together (via concurrently) |
| `npm run dev:backend` | Start only the FastAPI backend |
| `npm run dev:frontend` | Start only the Vite dev server |
| `npm run install:all` | Install frontend dependencies |
| `npm run build` | Build frontend for production |
| `npm run test` | Run backend pytest suite |
| `npm run package` | Build standalone .exe (Windows) |

### 3. Use It

1. Type a prompt describing your automation (e.g., "Open Notepad, type Hello World, save as test.txt")
2. Click **Generate Plan** — the AI creates a step-by-step action plan
3. Review the generated PyWinAuto code in the approval dialog
4. Click **Approve & Run** — the automation executes on your desktop with live progress
5. If a step fails, add notes in the refinement panel and click **Re-generate Plan**
6. Once it works, click **Save Script** to store it in your library

## Packaged .exe (Single-File Distribution)

Build a standalone Windows executable that bundles the backend and frontend together:

```bash
cd win-auto
python build/build.py
```

This produces `dist/win-auto.exe` (~80-120 MB). To use it:

```
C:\MyFolder\
  win-auto.exe
  .env              <-- create this file with your ANTHROPIC_API_KEY
```

Run `win-auto.exe` — it starts the server and serves the UI at `http://localhost:8000`.

## Configuration

All settings are configured via `.env` (or environment variables):

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | *(required)* | Your Anthropic API key |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-20250514` | Claude model to use |
| `SERVER_HOST` | `0.0.0.0` | Server bind address |
| `SERVER_PORT` | `8000` | Server port |
| `DATABASE_URL` | `sqlite:///data/win-auto.db` | SQLite database path |
| `EXECUTION_TIMEOUT_SECONDS` | `300` | Max execution time per run |
| `SCREENSHOT_RETENTION_DAYS` | `30` | Auto-delete screenshots older than this |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌────────┐ │
│  │  Prompt   │→ │   Plan   │→ │   Code    │→ │  Live  │ │
│  │  Editor   │  │  Viewer  │  │  Review   │  │Progress│ │
│  └──────────┘  └──────────┘  └───────────┘  └────────┘ │
│         │              ↑             ↑           ↑       │
└─────────┼──────────────┼─────────────┼───────────┼───────┘
          │ POST         │ JSON        │ JSON      │ SSE
          ▼              │             │           │
┌─────────┼──────────────┼─────────────┼───────────┼───────┐
│         ▼              │             │           │        │
│  ┌────────────┐  ┌───────────┐  ┌─────────┐  ┌────────┐ │
│  │  /generate │  │  /scripts │  │/execute │  │/stream │ │
│  └─────┬──────┘  └───────────┘  └────┬────┘  └───┬────┘ │
│        │                              │           │      │
│        ▼                              ▼           │      │
│  ┌────────────┐  ┌───────────┐  ┌─────────┐      │      │
│  │    LLM     │  │   Code    │  │Executor │──────┘      │
│  │  Service   │  │ Validator │  │ Service │              │
│  │ (Claude)   │  │  (AST)   │  │ (mutex) │              │
│  └────────────┘  └───────────┘  └────┬────┘             │
│                                       │                  │
│                    Backend (FastAPI)   │                  │
└───────────────────────────────────────┼──────────────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │   Subprocess     │
                               │  (PyWinAuto      │
                               │   script.py)     │
                               │                  │
                               │  → JSON-line     │
                               │    stdout        │
                               │  → screenshots   │
                               └─────────────────┘
```

### Data Flow

1. **User prompt** → `POST /api/generate` → LLM Service calls Claude → returns structured JSON plan
2. **User approves** → Code Generator compiles plan into a PyWinAuto script → Code Validator checks AST for prohibited imports/patterns
3. **User runs** → `POST /api/execute` → Executor Service spawns subprocess with mutex lock (one execution at a time)
4. **Subprocess** runs the PyWinAuto script, emitting JSON-line progress on stdout and capturing screenshots via `mss`
5. **Frontend** connects to `GET /api/execute/{id}/stream` (SSE) for real-time step updates and screenshots
6. **On failure** → User adds notes in the Refinement Panel → `POST /api/generate/refine` sends original plan + error + notes back to Claude for a revised plan
7. **On success** → User saves the script to SQLite via `POST /api/scripts` → appears in Library tab

### Key Design Decisions

- **Subprocess isolation**: Generated scripts run in a separate Python process, not inside FastAPI. This prevents automation crashes from taking down the server.
- **Execution mutex**: Only one automation runs at a time. Concurrent requests get HTTP 409. This avoids UI element conflicts on the desktop.
- **AST-based validation**: Before execution, generated code is parsed into an AST and checked against an import allowlist and prohibited pattern list (no shell commands, no network calls, no dynamic code execution).
- **JSON-line protocol**: The subprocess communicates via structured JSON lines on stdout (`{"type": "step_start", ...}`), making progress parsing reliable and language-agnostic.
- **SSE streaming**: Server-Sent Events provide one-directional real-time updates without WebSocket complexity.

## Project Structure

```
win-auto/
├── backend/
│   ├── main.py                 # FastAPI server with lifespan management
│   ├── config.py               # Settings from .env via pydantic-settings
│   ├── db/                     # SQLAlchemy models + Alembic migrations
│   ├── services/
│   │   ├── llm_service.py      # Anthropic Claude integration
│   │   ├── code_generator.py   # Plan → PyWinAuto code compiler
│   │   ├── code_validator.py   # AST-based security validation
│   │   └── executor_service.py # Subprocess manager with mutex
│   ├── routes/                 # API endpoints (scripts, generate, execute)
│   ├── executor/               # Helpers for subprocess reporting + screenshots
│   └── tests/                  # 30 tests across 7 files
├── frontend/
│   ├── src/
│   │   ├── pages/              # CreatePage (workflow), LibraryPage (saved scripts)
│   │   ├── components/         # PromptEditor, PlanViewer, CodeReviewDialog, etc.
│   │   └── api/                # TypeScript API client + types
│   └── ...                     # Vite + React + Tailwind config
└── build/                      # PyInstaller packaging
```

## How It Works

1. **Prompt → Plan:** Your natural language prompt is sent to Claude, which returns a structured JSON action plan (open app, click element, type text, etc.)
2. **Plan → Code:** The plan is compiled into a runnable PyWinAuto Python script with per-step error handling and screenshot capture
3. **Security Gate:** Generated code is validated via AST analysis — only approved imports and operations are allowed
4. **Execution:** The script runs in an isolated subprocess. Progress streams to the UI via Server-Sent Events (SSE)
5. **Refinement:** If a step fails, you see the error + screenshot and can add notes. The AI generates an improved plan incorporating your feedback
6. **Save:** Working automations are saved to SQLite and appear in the Library tab for re-use

## Running Tests

```bash
# From win-auto root:
npm test

# Or directly:
cd win-auto/backend
python -m pytest tests/ -v
```
