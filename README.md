# CRAB Webapp (Code Review Automation Benchmark)

A research-driven platform for evaluating deep learning models on automated code review tasks. CRAB provides two core services:

- **Dataset download**: Obtain high-quality, curated Java code review datasets for **comment
  generation** and **code refinement** tasks.
- **Result evaluation**: Upload model-generated predictions to receive standardized evaluation
  metrics via a REST+WebSocket API.

## Features

- **Static Frontend**: Vanilla HTML/CSS/JS interface—no build toolchain required.
- **Dataset Delivery**: ZIP archives of JSON files, with optional full repo context.
- **Submission Queue**: Server-managed job queue with configurable parallelism (via `MAX_WORKERS`).
- **Real‑time Feedback**: Progress updates over WebSockets (using Flask-SocketIO).
- **Robust Data Processing**: Utilities for parsing, validating, and evaluating submissions in `src/utils`.

## Prerequisites

- **Python 3.8+**
- *(Optional)* Docker daemon if you wish to execute the code refinement evaluation

## Installation & Setup

1. **Clone** the repository:

   ```bash
   git clone https://github.com/karma-riuk/crab-webapp.git
   cd crab-webapp
   ```

1. **Install** Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Environment Variables

Defaults are set in `src/utils/env_defaults.py` (port 45003, `data/` path, etc.) To override:

```bash
cp .env.example .env
# Edit .env to adjust:
# PORT=..., MAX_WORKERS=..., DATA_PATH=..., RESULTS_DIR=...
```

## Running the Application

From the project root:

```bash
python src/server.py
```

- The Flask app serves static files from `public/` at `/` and mounts API routes under `/datasets` and `/answers` via Blueprints.
- By default, open your browser to **[http://localhost:45003/](http://localhost:45003/)**.

## API Endpoints

| Method | Route | Description |
| ------ | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| GET | `/datasets/download/<dataset>` | Download ZIP of `comment_generation` or `code_refinement` (use `?withContext=true` for full repo).|
| POST | `/answers/submit/comment` | Submit comment-generation JSON. |
| POST | `/answers/submit/refinement` | Submit code-refinement JSON. |
| GET | `/answers/status/<id>` | Poll status or results (may include `X-Socket-Id` for notifications). |

## Project Structure

```
├── data/                       # Dataset files: dataset.json, archives, etc.
├── public/                     # Static frontend
│   ├── css/style.css           # Styles
│   ├── img/crab.png            # Icon
│   ├── index.html              # UI with modals, schema docs
│   └── js/                     # Frontend scripts
│       ├── index.js            # UI logic, fetch & WebSocket handlers
│       ├── modal.js            # Modal dialogs
│       └── sorttable.js        # Table sorting
├── src/                        # Backend source
│   ├── server.py               # App entry: Flask + SocketIO
│   ├── routes/                 # Blueprints
│   │   ├── index.py            # Root & health-check
│   │   ├── datasets.py         # File downloads
│   │   └── answers.py          # Submission & status endpoints
│   └── utils/                  # Core logic & helpers
│       ├── env_defaults.py     # Default ENV vars
│       ├── dataset.py          # Load/validate dataset JSON
│       ├── process_data.py     # Evaluation functions
│       ├── observer.py         # WebSocket observer & queue cleanup
│       ├── queue_manager.py    # Concurrency control
│       └── build_handlers.py   # Build/test wrappers
├── requirements.txt            # Python libs: Flask, SocketIO, dotenv, etc.
├── TODO.md                     # Next steps and backlog
└── .env.example                # Template for environment variables
```

## Contributing

1. **Issue Tracker**: Please file issues for bugs or feature requests.
1. **Pull Requests**: Fork, create a topic branch, and submit a PR. Please include tests or validations where applicable.

## Acknowledgements

- Developed as part of a Master's thesis at Università della Svizzera Italiana.
