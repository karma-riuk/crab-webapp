# CRAB Webapp (Code Review Automation Benchmark)

A research-driven platform for evaluating deep learning models on automated code review tasks. CRAB provides two core services:

- **Dataset download**: Obtain high-quality, curated Java code review datasets for **comment
  generation** and **code refinement** tasks.
- **Result evaluation**: Upload model-generated predictions to receive standardized evaluation
  metrics via a REST+WebSocket API.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
  - [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Using the Webapp](#using-the-webapp)
  - [Download a Dataset](#download-a-dataset)
  - [Upload Predictions](#upload-predictions)
  - [Track Submission Status](#track-submission-status)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Acknowledgements](#acknowledgements)

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

## Using the Webapp

### Download a Dataset

1. Select **Comment Generation** or **Code Refinement**.
1. (Optional) Check **Include context** to get full repo snapshots.
1. Click **Download** to receive a ZIP with JSON (see schemas in `public/index.html`)

### Upload Predictions

1. Choose task type (`comment` or `refinement`).
1. Select your JSON file (matching the dataset schema).
1. Click **Upload JSON**.
1. The server responds with a **process ID**.

### Track Submission Status

- Progress bar displays real-time percentage via WebSocket events (requires `X-Socket-Id` for subscribing to updates).

- You can also poll **GET** `/answers/status/<id>` to retrieve a simple JSON object:

  - `status`: `created`, `waiting`, `processing`, or `complete`

  - Once `status` is `complete`, the response includes:

    ```js
    {
      "type": "comment" | "refinement",
      "results": { /* evaluation metrics or processed data */ }
    }
    ```

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

## Acknowledgements

- Developed as part of a Master's thesis at Università della Svizzera Italiana.
