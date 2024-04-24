from typing import Annotated

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from .env import Settings

config = Settings()

token_scheme = APIKeyHeader(name="x-api-key", auto_error=False)


async def verify_token(token: Annotated[str, Security(token_scheme)]):
    if token not in config.api_tokens:
        raise HTTPException(status_code=403, detail="Unauthorized!")
