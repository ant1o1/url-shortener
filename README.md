# url-shortener
A simple FastAPI-based URL shortener that generates short slugs for redirects.

## Local deployment

### Install mise
https://mise.jdx.dev/getting-started.html

### Set up and activate the environment
```bash
cd url-shortener
mise trust
```
Specific version of Python and Poetry will be installed in the current folder, and a Python virtual environment will be created and activated.

### Install dependencies
```bash
poetry install
```

### Run the app
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
The app will be available on http://localhost:8000.

## Docker deployment

### Build the image
```bash
docker build -t url-shortener .
```

### Create .env file
```bash
cp .env.example .env
```

### Run the app
```bash
docker run --name url-shortener --env-file .env -p 8000:8000 url-shortener
```
The app will be available on http://localhost:8000.

## Run tests (local deployment only)
```bash
pytest
```
Tests remain to be implemented.

## Documentation
Interactive documentation is available on:
* http://localhost:8000/docs (Swagger UI)
* http://localhost:8000/redoc (Redoc)
