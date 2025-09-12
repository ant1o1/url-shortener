import os

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    MetaData,
    RowMapping,
    String,
    Table,
    Text,
    create_engine,
    func,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError

# Use environment variable for DB, defaulting to local SQLite file
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///url_shortener.db")

engine = create_engine(
    DATABASE_URL,
)

metadata = MetaData()

# Define the "urls" table schema
urls = Table(
    "urls",
    metadata,
    Column("slug", String(6), primary_key=True),
    Column("long_url", Text, nullable=False),
    Column(
        "created_at", DateTime(timezone=True), server_default=func.now(), nullable=False
    ),
    Column("clicks", Integer, nullable=False, server_default="0"),
)


def init_db() -> None:
    """Initialize the database schema.

    Creates all tables defined in the metadata if they don't exist.
    """
    metadata.create_all(engine)


def shutdown_db() -> None:
    """Close database connections.

    Disposes of the SQLAlchemy engine and releases resources.
    """
    engine.dispose()


def get_url_by_slug(slug: str) -> RowMapping | None:
    """Retrieve a URL record by its slug.

    Args:
        slug (str): Shortened URL slug.

    Returns:
        RowMapping | None: Dictionary-like row mapping containing slug, long_url,
        created_at, and clicks. Returns None if not found.
    """
    stmt = select(urls).where(urls.c.slug == slug)
    with engine.connect() as conn:
        result = conn.execute(stmt).mappings().first()
        return result


def increment_clicks(slug: str) -> None:
    """Increment the click counter for a slug.

    Args:
        slug (str): Shortened URL slug.
    """
    stmt = update(urls).where(urls.c.slug == slug).values(clicks=urls.c.clicks + 1)
    with engine.begin() as conn:  # begin() ensures transaction management
        conn.execute(stmt)


def create_url(slug: str, long_url: str) -> None:
    """Insert a new URL mapping into the database.

    Args:
        slug (str): Unique short slug identifier.
        long_url (str): The original long URL.

    Raises:
        IntegrityError: If the slug already exists in the database.
    """
    stmt = urls.insert().values(
        slug=slug,
        long_url=long_url,
    )
    try:
        with engine.begin() as conn:
            conn.execute(stmt)
    except IntegrityError:
        # Let caller handle collisions (e.g., retry with another slug)
        raise
