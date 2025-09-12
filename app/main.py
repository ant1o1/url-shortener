from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import HttpUrl
from sqlalchemy.exc import IntegrityError

from app.db import create_url, get_url_by_slug, increment_clicks, init_db, shutdown_db
from app.models import ShortenIn, ShortenOut, Slug
from app.utils import generate_slug


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage DB connection lifecycle.

    Args:
        app (FastAPI): The FastAPI application.
    """
    init_db()
    yield
    shutdown_db()


app = FastAPI(
    title="URL Shortener",
    version="0.1.0",
    description="A simple FastAPI-based URL shortener that generates short slugs for redirects.",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    """Health check endpoint.

    Returns:
        dict: {"status": "ok"}
    """
    return {"status": "ok"}


@app.post(
    "/api/shorten",
    response_model=ShortenOut,
    status_code=status.HTTP_201_CREATED,
)
def create_short_url(payload: ShortenIn, request: Request) -> ShortenOut:
    """Create or return a shortened URL for the given long URL.

    Args:
        payload (ShortenIn): Input containing the long URL to shorten.
        request (Request): FastAPI request object for base URL.

    Raises:
        HTTPException: HTTPException: 500 if no unique slug can be allocated.

    Returns:
        ShortenOut: Object containing slug and shortened URL.
    """
    url = str(payload.url)

    for attempt in range(10):  # Retry on collision
        slug = generate_slug(url, attempt)

        try:
            create_url(slug=slug, long_url=url)
            return ShortenOut(
                slug=slug,
                short_url=HttpUrl(str(request.base_url.replace(path=slug))),
            )
        except IntegrityError:
            url_in_db = get_url_by_slug(slug)
            if url_in_db and url_in_db["long_url"] == url:
                return ShortenOut(
                    slug=slug, short_url=HttpUrl(str(request.base_url) + slug)
                )

    raise HTTPException(status_code=500, detail="Could not allocate a unique slug")


@app.get("/{slug}", include_in_schema=False)
def redirect_slug(slug: Slug) -> RedirectResponse:
    """Redirect from slug to original long URL.

    Args:
        slug (Slug): Shortened URL slug.

    Raises:
        HTTPException: 404 if slug not found in database.

    Returns:
        RedirectResponse: 302 redirect to the original long URL.
    """
    url = get_url_by_slug(slug=slug)
    if url is None:
        raise HTTPException(status_code=404, detail="URL not found")

    increment_clicks(slug)
    return RedirectResponse(url=url["long_url"], status_code=status.HTTP_302_FOUND)
