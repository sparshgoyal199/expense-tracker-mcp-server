# # auth.py
# import os
# from fastmcp.server.auth.providers.supabase import SupabaseProvider

# def create_supabase_auth() -> SupabaseProvider:
#     return SupabaseProvider(
#         project_url=os.environ["SUPABASE_PROJECT_URL"],  # e.g. https://abc123.supabase.co
#         base_url=os.environ["FASTMCP_BASE_URL"],          # e.g. http://localhost:8003
#         algorithm=os.environ.get("SUPABASE_JWT_ALGORITHM", "ES256"),
#     )

# auth.py
import os
from functools import lru_cache
from typing import Annotated

import httpx
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import JWTError, jwt
from pydantic import BaseModel

load_dotenv()
# The issuer includes /auth/v1 — this is what Supabase puts in the token
ISSUER = f"{os.environ['SUPABASE_PROJECT_URL']}/auth/v1"
JWKS_URL = f"{os.environ['SUPABASE_PROJECT_URL']}/auth/v1/.well-known/jwks.json"

# The audience for an authenticated user is "authenticated"
AUDIENCE = "authenticated"

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{ISSUER}/oauth/authorize",
    tokenUrl=f"{ISSUER}/oauth/token",
)


class User(BaseModel):
    id: str
    email: str | None = None


@lru_cache(maxsize=1)
def get_jwks() -> dict:
    """Fetches and caches the JWKS from Supabase."""
    response = httpx.get(JWKS_URL)
    response.raise_for_status()
    return response.json()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """Verifies the JWT access token and returns the user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        jwks = get_jwks()
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["ES256", "RS256"],
            audience=AUDIENCE,      # "authenticated"
            issuer=ISSUER,          # https://...supabase.co/auth/v1
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return User(id=user_id, email=payload.get("email"))
    except JWTError as e:
        # Print the actual error to the terminal so you can see what's wrong
        print(f"JWT verification failed: {e}")
        raise credentials_exception