from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import HttpUrl
from sqlalchemy.exc import IntegrityError

from app.db import create_url, get_url_by_slug, increment_clicks, init_db, shutdown_db
from app.models import ShortenedUrl, ShortenIn, ShortenOut, Slug
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


@app.get(
    "/health",
    description="Health check endpoint.",
    responses={503: {"description": "Service not healthy"}},
)
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post(
    "/api/shorten",
    response_model=ShortenOut,
    status_code=status.HTTP_201_CREATED,
    description="Create or return a shortened URL for the given long URL.",
    responses={
        400: {"description": "Invalid URL"},
        409: {"description": "Slug already used"},
        500: {"description": "Could not allocate a unique slug"},
    },
)
def create_short_url(payload: ShortenIn, request: Request) -> ShortenOut:
    """Create or return a shortened URL for the given long URL."""
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


@app.get(
    "/{slug}",
    include_in_schema=False,
    response_class=RedirectResponse,
    description="Redirect from slug to original long URL.",
    responses={
        302: {"description": "Redirect to the original long URL"},
        404: {"description": "URL not found"},
    },
)
def redirect_slug(slug: Slug) -> RedirectResponse:
    """Redirect from slug to original long URL."""
    url = get_url_by_slug(slug=slug)
    if url is None:
        raise HTTPException(status_code=404, detail="URL not found")

    increment_clicks(slug)
    return RedirectResponse(url=url["long_url"], status_code=status.HTTP_302_FOUND)


@app.get(
    "/api/{slug}",
    response_model=ShortenedUrl,
    description="Retrieve metadata for a shortened URL.",
    responses={
        404: {"description": "URL not found"},
    },
)
def get_url_info(slug: Slug) -> ShortenedUrl:
    url = get_url_by_slug(slug=slug)
    if url is None:
        raise HTTPException(status_code=404, detail="URL not found")

    return ShortenedUrl(
        slug=slug,
        long_url=url["long_url"],
        created_at=url["created_at"],
        clicks=url["clicks"],
    )
