import ipaddress
from datetime import datetime
from typing import Annotated

from fastapi import Path
from pydantic import BaseModel, HttpUrl, field_validator

Slug = Annotated[str, Path(pattern=r"^[A-Za-z0-9]{6}$")]


class ShortenIn(BaseModel):
    url: HttpUrl

    @field_validator("url")
    @classmethod
    def disallow_ip_and_localhost(cls, v: HttpUrl):
        host = v.host or ""
        try:
            # If this succeeds, it's an IP
            ipaddress.ip_address(host)
        except ValueError:
            # Not an IP, that's fine
            pass
        else:
            # No exception: it's a valid IP
            raise ValueError("IP hosts are not allowed.")

        if host.lower() == "localhost":
            raise ValueError("localhost is not allowed.")

        return v


class ShortenOut(BaseModel):
    slug: Slug
    short_url: HttpUrl


class ShortenedUrl(BaseModel):
    slug: Slug
    long_url: HttpUrl
    created_at: datetime
    clicks: int = 0
