# Locator Lense

Local/demo MVP for analyzing static HTML and generating element locators.

## Run

Create and activate the project virtual environment, then install dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Start the Flask app:

```powershell
.\.venv\Scripts\python.exe app.py
```

Open `http://127.0.0.1:5000/` and submit either a URL or raw HTML, but not both.

## Test

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The MVP analyzes server-delivered static HTML only. It does not execute JavaScript
or provide production SSRF protection, advanced resource controls, rate limiting,
authentication, or background processing.