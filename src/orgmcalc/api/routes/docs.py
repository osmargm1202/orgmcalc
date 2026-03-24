"""Documentation routes - serve external API documentation."""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

router = APIRouter(tags=["documentation"])

# Path to the markdown documentation file
DOCS_PATH = Path(__file__).parent.parent.parent.parent.parent / "externo" / "api.md"


@router.get("/externo/api-md", response_class=PlainTextResponse)
async def get_api_documentation() -> str:
    """Serve the API documentation in Markdown format.

    Returns:
        The full API documentation as markdown text.

    Raises:
        HTTPException: 503 if documentation file is not available.

    """
    if not DOCS_PATH.exists():
        raise HTTPException(status_code=503, detail="Documentation not available")
    return DOCS_PATH.read_text(encoding="utf-8")
