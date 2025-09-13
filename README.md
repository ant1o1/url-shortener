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
uvicorn app.main:app --host 0.0.0.0 --port 80
```
The app will be available on http://localhost.

## Docker deployment

### Build the image
```bash
docker build -t url-shortener .
```

### Run the app
```bash
docker run --name url-shortener -p 80:80 url-shortener
```
The app will be available on http://localhost.

## Run tests (local deployment only)
```bash
pytest
```
Tests remains to be implemented.

## Documentation
Interactive documentation is available on:
* http://localhost/docs (Swagger UI)
* http://localhost/redoc (Redoc)
