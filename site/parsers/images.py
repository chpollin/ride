"""Image URL rewriting from WordPress CDN to local paths."""

import re
from pathlib import Path


# Matches WordPress CDN URLs for RIDE images
WP_PATTERN = re.compile(
    r"https?://ride\.i-d-e\.de/wp-content/uploads/issue_(\d+)/([^/]+)/pictures/(.+?)$"
)


def rewrite_image_url(url: str, review_slug: str) -> str:
    """Convert WordPress CDN URL to a relative local path.

    Returns a path relative to the review's output directory,
    e.g., 'pictures/picture-1.png'
    """
    match = WP_PATTERN.match(url)
    if not match:
        return url  # External URL or already local

    filename = match.group(3)
    # Ensure the filename has an extension
    if not Path(filename).suffix:
        filename = filename + ".png"

    return f"pictures/{filename}"


def resolve_local_image(pictures_dir: Path, filename: str) -> str:
    """Resolve an image filename against the local filesystem,
    handling case-insensitive matching and missing extensions.

    Returns the actual filename found on disk, or the original if not found.
    """
    if not pictures_dir.exists():
        return filename

    # Try exact match first
    target = pictures_dir / filename
    if target.exists():
        return filename

    # Try case-insensitive match
    name_lower = filename.lower()
    for f in pictures_dir.iterdir():
        if f.name.lower() == name_lower:
            return f.name

    # Try without extension, then add common ones
    stem = Path(filename).stem
    for ext in [".png", ".PNG", ".jpg", ".JPG", ".jpeg"]:
        candidate = pictures_dir / (stem + ext)
        if candidate.exists():
            return stem + ext

    return filename


def list_image_files(pictures_dir: Path) -> list[str]:
    """List all image files in a pictures directory."""
    if not pictures_dir.exists():
        return []
    image_exts = {".png", ".jpg", ".jpeg", ".gif", ".svg"}
    return sorted(
        f.name for f in pictures_dir.iterdir()
        if f.suffix.lower() in image_exts
    )
