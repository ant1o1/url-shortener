import hashlib


def generate_slug(url: str, attempt: int) -> str:
    """Generate a short slug from a URL and attempt number.

    Args:
        url (str): The original long URL to shorten.
        attempt (int): Retry attempt number, used to avoid collisions.

    Returns:
        str: A 6-character slug derived from the MD5 hash of the URL and attempt.
    """
    md5_hash = hashlib.md5(f"{url}|{attempt}".encode()).hexdigest()
    print(f"{url}|{attempt}".encode())
    return md5_hash[:6]
