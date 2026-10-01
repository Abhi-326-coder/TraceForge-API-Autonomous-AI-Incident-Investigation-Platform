## Create a folder by name - backend

Move into backend:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

You should see something like:

```bash
(.venv) C:\...\traceforge\backend>
```

Check Python:

```bash
python --version
```

I'd recommend Python 3.11+.

Then upgrade pip:

```bash
python -m pip install --upgrade pip
```

## Install FastAPI

We're intentionally starting with only FastAPI.

```bash
pip install fastapi uvicorn
```

Then:

```bash
pip freeze > requirements.txt
```