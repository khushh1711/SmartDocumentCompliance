# Smart Document Compliance & Contract Clause Checker

A Python-based RPA project that automates parts of the contract-review
workflow. It combines a React web interface, a FastAPI backend, and a
Python folder-monitoring bot to analyze contracts, produce compliance
reports, organize processed files, and maintain a CSV processing log.

> **Important:** This project provides preliminary, rule-based contract
> checking. It is not legal advice and does not guarantee that a
> contract is legally compliant. Detected headings or keywords do not
> necessarily prove that a clause is complete or legally sufficient.

------------------------------------------------------------------------

## Table of Contents

-   [Overview](#overview)
-   [Key Features](#key-features)
-   [How the System Works](#how-the-system-works)
-   [Architecture](#architecture)
-   [Technology Stack](#technology-stack)
-   [Project Structure](#project-structure)
-   [Prerequisites](#prerequisites)
-   [Run the Project Locally](#run-the-project-locally)
-   [How to Use the Project](#how-to-use-the-project)
-   [API Endpoints](#api-endpoints)
-   [Automation Workflow](#automation-workflow)
-   [Processing Log and Dashboard](#processing-log-and-dashboard)
-   [Troubleshooting](#troubleshooting)
-   [Current Limitations](#current-limitations)
-   [Possible Future Improvements](#possible-future-improvements)
-   [Notes for Contributors](#notes-for-contributors)

------------------------------------------------------------------------

## Overview

Manual contract checking can involve repeatedly searching for important
clauses, reviewing the document, preparing a report, moving files, and
maintaining records. This project automates several of those repetitive
steps.

The system checks for configured contract clause categories, calculates
a compliance score and risk classification according to the implemented
rules, and generates a PDF report. Its automation bot can monitor an
incoming folder and submit new documents to the backend without
requiring the user to upload each file through the website.

The project has two main ways to start contract analysis:

1.  **Web-based analysis:** A user submits a contract through the React
    frontend.
2.  **Folder-based automation:** A user places a contract in the
    incoming folder while the Python automation bot is running.

The project also includes a dashboard backed by a CSV processing log.

## Key Features

-   **Contract Analyzer UI:** Submit a contract through the web
    interface and review the returned analysis.
-   **Clause detection:** Checks configured categories such as:
    -   Confidentiality
    -   Termination
    -   Payment
    -   Data Protection
    -   Governing Law
    -   Dispute Resolution
-   **Evidence extraction:** Attempts to extract text associated with
    detected clauses.
-   **Compliance score and risk category:** Calculates results using the
    rules implemented in the backend.
-   **PDF report generation:** Produces a report for the processed
    contract.
-   **Incoming-folder monitoring:** The automation bot periodically
    checks for documents to process.
-   **Automatic file organization:** After a successful API response,
    the bot moves the processed contract to the processed folder.
-   **Report organization:** The bot attempts to move generated reports
    into the reports folder.
-   **CSV processing log:** Stores processing information for tracking.
-   **Dashboard:** Reads the log through the backend and presents
    processing statistics and records.

> Exact supported document formats, score formula, risk thresholds, PDF
> fields, and CSV column names depend on the current source code. Check
> the implementation before documenting or changing those details.

## How the System Works

### Option A: Automated folder-based processing

1.  Start the FastAPI backend.
2.  Start the automation bot in a separate terminal.
3.  Place a contract file in `contracts/incoming/`.
4.  The bot periodically checks the incoming folder.
5.  When it detects a file to process, it sends the document to the
    backend's `/upload` endpoint at `http://127.0.0.1:8000/upload`.
6.  The backend runs the configured document-processing and
    clause-detection logic.
7.  The backend calculates the compliance score and risk classification
    according to its rules and generates a PDF report.
8.  When the request is successful, the bot moves the original contract
    into `contracts/processed/`.
9.  The bot attempts to move generated reports into
    `contracts/reports/`.
10. Processing information is recorded in
    `contracts/processing_log.csv`.
11. The dashboard reads processing data through the `/dashboard`
    endpoint.

The backend and bot must remain running for this workflow to continue.
The frontend is only required if someone wants to use the website or
view the dashboard.

### Option B: Manual web-based analysis

1.  Start the backend.
2.  Start the frontend.
3.  Open the local URL printed by Vite in the terminal.
4.  Open the Contract Analyzer view.
5.  Select and submit a contract using the interface.
6.  The frontend sends the document to the backend.
7.  Review the analysis returned by the backend and the generated
    report, where available in the UI.

The manual-upload path may not use the same file-moving and logging
behavior as the automation-bot path. Verify the current implementation
if you need to know whether every manual upload appears in the
dashboard.

## Architecture

``` mermaid
flowchart TD
    U[User] -->|Manual upload| FE[React + Vite Frontend]
    FE -->|HTTP request| API[FastAPI Backend]
    IN[contracts/incoming] --> BOT[Python Automation Bot]
    BOT -->|POST document to /upload| API
    API --> DET[Clause Detection and Evidence Extraction]
    DET --> SCORE[Compliance Score and Risk Classification]
    SCORE --> PDF[PDF Report Generation]
    API -->|Response| FE
    BOT -->|After successful processing| PROC[contracts/processed]
    PDF -.->|Bot attempts to organize report| REP[contracts/reports]
    BOT --> LOG[contracts/processing_log.csv]
    LOG --> API
    API -->|GET /dashboard data| DASH[Dashboard in Frontend]
```

### Component responsibilities

  -----------------------------------------------------------------------
  Component                           Responsibility
  ----------------------------------- -----------------------------------
  React frontend                      Provides the Contract Analyzer and
                                      Dashboard interface.

  FastAPI backend                     Accepts document submissions, runs
                                      the implemented analysis workflow,
                                      and provides dashboard data.

  Python automation bot               Monitors the incoming folder,
                                      submits files to the backend, and
                                      organizes files/logs after
                                      processing.

  `contracts/incoming/`               Folder where documents are placed
                                      for automated processing.

  `contracts/processed/`              Destination for successfully
                                      processed original documents.

  `contracts/reports/`                Intended destination for generated
                                      reports organized by the bot.

  `contracts/processing_log.csv`      Stores processing records read by
                                      the dashboard.
  -----------------------------------------------------------------------

## Technology Stack

-   **Python:** Backend and automation implementation.
-   **FastAPI:** Backend API.
-   **Uvicorn:** Local ASGI server used to run FastAPI.
-   **React:** Frontend UI.
-   **Vite:** Frontend development server and tooling.
-   **JavaScript and CSS:** Frontend behavior and styling.
-   **HTTP requests:** Communication from the automation bot to the
    backend.
-   **CSV:** Basic processing history and dashboard data.
-   **PDF-generation library:** Used by the backend to generate reports;
    check `backend/main.py` to confirm the exact library.

This project uses a Python-based automation implementation. Do not
describe it as a UiPath or Automation Anywhere project unless one of
those tools has actually been added.

## Project Structure

The known core structure is:

``` text
SmartDocumentCompliance/
├── backend/
│   └── main.py
├── frontend/
│   └── src/
│       ├── App.jsx
│       └── App.css
├── automation/
│   └── automation.py
├── contracts/
│   ├── incoming/
│   ├── processed/
│   ├── reports/
│   └── processing_log.csv
└── venv/
```

Other files such as `frontend/package.json`, frontend public assets, and
Python dependency files may also exist. This tree shows the main project
components, not necessarily every file in the repository.

### Important paths

-   `backend/main.py` --- FastAPI app, upload endpoint, clause analysis,
    report generation, and dashboard endpoint.
-   `frontend/src/App.jsx` --- React application and main UI views.
-   `frontend/src/App.css` --- Frontend styling.
-   `automation/automation.py` --- Folder-monitoring bot.
-   `contracts/incoming/` --- Place files here for bot-based processing.
-   `contracts/processed/` --- Processed input files.
-   `contracts/reports/` --- Reports organized by the bot.
-   `contracts/processing_log.csv` --- Processing history.

The backend's report output path is determined by the path configured in
the code. Confirm it in `backend/main.py` and `automation/automation.py`
if you need to change where reports are saved or moved.

## Prerequisites

Install or confirm the following on your computer:

-   Python installed and compatible with the project's dependencies.
-   Node.js and npm installed.
-   The project dependencies already installed in the Python virtual
    environment and frontend directory.
-   The project folder available at:

``` text
C:\Users\DELL\Desktop\SmartDocumentCompliance
```

If you use a different computer or folder, replace the path in the
commands below with your actual project location.

## Run the Project Locally

Run each component in its **own terminal**. Keep the terminals open
while using the corresponding component.

### 1. Start the backend

Open Terminal 1 in PowerShell:

``` powershell
cd C:\Users\DELL\Desktop\SmartDocumentCompliance
.\venv\Scripts\activate
cd backend
uvicorn main:app --reload
```

The backend should be available at:

``` text
http://127.0.0.1:8000
```

FastAPI's interactive API documentation is usually available at:

``` text
http://127.0.0.1:8000/docs
```

Keep this terminal running. Both the frontend and automation bot depend
on the backend for processing.

### 2. Start the frontend

Open Terminal 2:

``` powershell
cd C:\Users\DELL\Desktop\SmartDocumentCompliance\frontend
npm run dev
```

Vite prints the local frontend URL in the terminal. It is commonly:

``` text
http://localhost:5173
```

Open the exact URL printed by Vite in your browser.

Keep this terminal running while using the website.

### 3. Start the automation bot

Open Terminal 3:

``` powershell
cd C:\Users\DELL\Desktop\SmartDocumentCompliance\automation
..\venv\Scripts\python.exe automation.py
```

Keep this terminal running for folder monitoring.

### Which components need to run?

  --------------------------------------------------------------------------------
  Task                               Backend           Frontend     Automation bot
  ----------------------- ------------------ ------------------ ------------------
  Analyze a document                Required           Required       Not required
  through the website                                           

  Automatically process             Required       Not required           Required
  files placed in                                               
  `contracts/incoming/`                                         

  Open and use the                  Required           Required    Not required to
  dashboard in the                                                         view it
  website                                                       

  Continue folder-based             Required           Optional           Required
  monitoring                                                    
  --------------------------------------------------------------------------------

The dashboard only shows records that the backend can read from the
processing log. It does not itself process incoming files.

## How to Use the Project

### Manual contract analysis

1.  Start the backend and frontend.
2.  Open the frontend URL.
3.  Navigate to the Contract Analyzer view.
4.  Select a supported document and submit it.
5.  Review the results returned by the backend.
6.  Review the generated report if the UI provides access to it.

The exact file formats accepted and the exact result fields are
determined by the current implementation.

### Automated contract analysis

1.  Start the backend.
2.  Start the automation bot.
3.  Copy a contract into `contracts/incoming/`.
4.  Wait for the bot to detect and submit it.
5.  Check the bot terminal for processing output.
6.  After successful processing, check `contracts/processed/` for the
    original document.
7.  Check `contracts/reports/` for an organized report.
8.  Check `contracts/processing_log.csv` for the processing record.
9.  Open the dashboard in the frontend to review available statistics.

If a file remains in the incoming folder, check whether the backend is
running and inspect the bot terminal for an error. The exact behavior on
failed requests depends on the bot's implementation.

## API Endpoints

The following endpoints are known to be part of the project:

  -----------------------------------------------------------------------
  Method                  Endpoint                Purpose
  ----------------------- ----------------------- -----------------------
  `POST`                  `/upload`               Accepts a contract for
                                                  processing. Used by the
                                                  frontend and automation
                                                  bot.

  `GET`                   `/dashboard`            Returns dashboard
                                                  statistics and
                                                  processing records from
                                                  the CSV log.
  -----------------------------------------------------------------------

The exact request fields, response schema, file validation, and error
responses should be checked in `backend/main.py` or through the local
API documentation at `http://127.0.0.1:8000/docs`.

## Automation Workflow

The automation bot is useful when multiple documents need to be
processed without manually submitting each one through the website.

### Direct automated actions

Once the backend and bot are running, the implemented workflow can
perform these actions automatically:

1.  Monitor the incoming folder.
2.  Detect files for processing.
3.  Send detected documents to `/upload`.
4.  Allow the backend to perform clause detection and analysis.
5.  Allow the backend to generate a PDF report.
6.  Move a successfully processed original document to the processed
    folder.
7.  Attempt to move generated reports to the reports folder.
8.  Record processing information in the CSV log.

Initial setup, starting the services, and placing files in the incoming
folder still require a person unless a separate mechanism has been
configured.

### Human-assisted actions

A person can: - Upload a contract through the website. - Review detected
clauses and extracted evidence. - Review the score and risk
classification. - Inspect the PDF report. - Review dashboard statistics
and records. - Decide whether a contract requires further manual or
professional review.

### How clause checking should be interpreted

The configured categories include Confidentiality, Termination, Payment,
Data Protection, Governing Law, and Dispute Resolution. The detection
logic uses the text and rules implemented in the backend. A matching
heading or keyword may produce a detection even when the full clause is
missing or incomplete. Always review the extracted evidence rather than
treating a positive match as proof of legal sufficiency.

## Processing Log and Dashboard

The automation workflow records processing information in:

``` text
contracts/processing_log.csv
```

The backend's `/dashboard` endpoint reads this log and returns fields
including:

-   `total_processed`
-   `low_risk`
-   `medium_risk`
-   `high_risk`
-   `records`

The React dashboard uses this response to display processing statistics
and records.

CSV is simple to inspect with a text editor or spreadsheet application,
but it is not a full database. For larger workloads or multiple
concurrent workers, a database and more robust audit logging may be
appropriate.

## Troubleshooting

### `Cannot connect to the Docker daemon`

Docker is not required to start the three components described in this
README unless you separately containerized the project. This error
usually means a Docker command was run while Docker was not available.
For the current local setup, use the Python, Uvicorn, and npm commands
above.

### `uvicorn` is not recognized

Confirm that the virtual environment is activated and that the project's
Python dependencies are installed. Run the backend command from the
`backend` directory after activating `venv`.

### `Cannot connect to the backend` or a request fails

-   Confirm that Terminal 1 is still running.
-   Check that the backend is listening on `http://127.0.0.1:8000`.
-   Look at the backend terminal for the actual error.
-   Confirm the frontend and bot are using the expected API URL.

### The frontend does not start

-   Confirm Node.js and npm are installed.
-   Run `npm run dev` from the `frontend` directory.
-   If dependencies have not been installed on this machine, run
    `npm install` in that directory.

### The automation bot does not process an incoming file

-   Confirm the bot terminal is still running.
-   Confirm the document is in the correct `contracts/incoming/`
    directory.
-   Confirm the backend is running.
-   Check the bot terminal for an API or file-handling error.
-   Check whether the file was moved to `contracts/processed/` after a
    successful response.

### The report is not in `contracts/reports/`

The bot attempts to move reports from the output directory configured in
the code. Check the backend report output path, the bot's source and
destination paths, and the backend response before assuming report
generation succeeded.

### Dashboard statistics are missing or incorrect

-   Confirm that `contracts/processing_log.csv` exists and contains
    processing records.
-   Confirm that the backend resolves the CSV path correctly.
-   Check the backend terminal for CSV-reading errors.
-   Verify the log's actual columns and how the endpoint counts risk
    categories.

### Clause evidence looks incomplete or incorrect

The current detection and evidence extraction logic may match headings,
keywords, or short text fragments. This is a limitation of the
implemented extraction rules, not a guarantee that the underlying
contract is compliant. Inspect the source text and improve the
extraction rules when necessary.

## Current Limitations

-   Clause detection depends on the implemented rules and document text
    extraction.
-   Keyword or heading matches may cause false positives or provide
    incomplete evidence.
-   The compliance score and risk classification represent the project's
    implemented logic, not a certified legal assessment.
-   The automation bot depends on the backend being available.
-   The local folder-monitoring workflow requires the bot to remain
    running.
-   CSV logging is suitable for a prototype but has limitations for
    concurrent or large-scale processing.
-   Supported formats, file-size limits, authentication, OCR, duplicate
    detection, retries, and deployment capabilities should not be
    assumed unless implemented and tested.
-   The web upload workflow and bot workflow may have different file
    movement or logging behavior.

## Possible Future Improvements

These are possible enhancements, not claims about current functionality:

-   Improve clause evidence extraction and reduce false positives.
-   Add stronger document parsing for more contract formats.
-   Add OCR for scanned documents.
-   Add duplicate-file detection and safer retry handling.
-   Improve error reporting and recovery.
-   Use a database for processing history.
-   Add user authentication and role-based access controls.
-   Add dashboard search, filters, and export options.
-   Add notifications for failed processing.
-   Make compliance rules configurable.
-   Add a human approval or review workflow.
-   Improve security and deployment readiness.

## Notes for Contributors

If you are working on this project with another team member:

1.  **Backend changes:** Start by checking `backend/main.py`. Keep the
    API request and response behavior consistent with the frontend and
    automation bot.
2.  **Frontend changes:** Check `frontend/src/App.jsx` and
    `frontend/src/App.css`. Verify the API URL used by the frontend.
3.  **Automation changes:** Check `automation/automation.py`. Be careful
    when changing incoming, processed, reports, or CSV paths.
4.  **Shared workflow:** If you change `/upload`, check both the
    frontend upload code and the bot's HTTP request. Both depend on the
    endpoint's behavior.
5.  **Dashboard changes:** If you change the CSV columns or risk labels,
    update the backend's `/dashboard` logic and the frontend display
    together.
6.  **Test changes:** Test manual upload and folder-based processing
    separately. Success in one workflow does not automatically prove
    that the other works.
7.  **Sensitive files:** Do not commit real contracts, confidential
    reports, API secrets, local virtual environments, or unnecessary
    generated files to a public repository. Review `.gitignore` before
    pushing.

### Quick start checklist

-   [ ] Backend starts successfully.
-   [ ] Frontend starts successfully.
-   [ ] Manual contract upload works.
-   [ ] Clause results and score are returned.
-   [ ] PDF report is generated.
-   [ ] Automation bot starts successfully.
-   [ ] A file placed in `contracts/incoming/` is processed.
-   [ ] Processed contract is moved to the expected folder.
-   [ ] Report organization works.
-   [ ] CSV log is updated.
-   [ ] Dashboard displays the expected statistics.

------------------------------------------------------------------------

## Project Summary

**Smart Document Compliance & Contract Clause Checker** is a
Python-based RPA prototype that combines a React frontend, FastAPI
backend, and folder-monitoring automation bot. It supports manual and
automated contract submission, rule-based clause checking, compliance
scoring, PDF report generation, file organization, CSV logging, and
dashboard reporting. Its purpose is to reduce repetitive
document-handling tasks and support human review---not to replace
professional legal judgment.
