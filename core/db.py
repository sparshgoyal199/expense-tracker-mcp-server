from supabase import create_async_client, AsyncClient
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase_client: AsyncClient | None = None   # abhi None, lifespan mein set hoga


async def init_supabase_client():
    global supabase_client
    supabase_client = await create_async_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase_client

from fastmcp.server.dependencies import get_access_token

async def get_or_create_user() -> str:
    """Current authenticated user ka internal Supabase id (uuid) return karta hai,
    WorkOS sub se lookup/create karke."""
    token = get_access_token()
    sub = token.claims["sub"]

    existing = await supabase_client.table("users") \
        .select("id") \
        .eq("workos_user_id", sub) \
        .execute()

    if existing.data:
        return existing.data[0]["id"]

    created = await supabase_client.table("users") \
        .insert({"workos_user_id": sub}) \
        .execute()
    return created.data[0]["id"]