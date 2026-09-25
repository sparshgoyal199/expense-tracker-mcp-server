"""
Simple OpenID Connect demo using WorkOS AuthKit, with PKCE (Proof Key for
Code Exchange) since this app has no client_secret.

Flow:
  1. GET  /login       -> generate a code_verifier + code_challenge,
                          redirect user to WorkOS's authorize page
  2. GET  /callback    -> WorkOS redirects here with a `code`; we exchange
                          it for tokens (using code_verifier instead of a
                          client secret), verify the ID token, save the
                          user's claims in a signed session cookie
  3. GET  /api/protected -> only works if session cookie is valid; returns
                          the token claims as JSON (this is our "resource
                          server" acting on itself)
  4. GET  /logout      -> clears the session

No database. No third party involved. client == resource server.
"""

import base64
import hashlib
import os
import secrets

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from jose import jwt
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ["CLIENT_ID"]
AUTHKIT_DOMAIN = os.environ["AUTHKIT_DOMAIN"].rstrip("/")
REDIRECT_URI = os.environ["REDIRECT_URI"]
SESSION_SECRET = os.environ["SESSION_SECRET"]

AUTHORIZE_URL = f"{AUTHKIT_DOMAIN}/oauth2/authorize"
TOKEN_URL = f"{AUTHKIT_DOMAIN}/oauth2/token"
JWKS_URL = f"{AUTHKIT_DOMAIN}/oauth2/jwks"

app = FastAPI()

# SessionMiddleware stores session data in a signed cookie (no server-side
# store needed for this demo). secret_key is just for signing that cookie.
# IMPORTANT: this must be a FIXED value from .env, not generated at random
# on every startup -- otherwise a reload mid-flow invalidates old sessions
# and every /callback fails with "invalid state".
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.get("/login")
def login(request: Request):
    # `state` protects against CSRF: we generate a random value, remember
    # it in the session, and check it matches when WorkOS redirects back.
    state = secrets.token_urlsafe(16)

    # --- PKCE setup ---
    # code_verifier: a random secret only we (and WorkOS) ever see.
    # code_challenge: a hash of code_verifier, sent up front in the
    #   authorize request. Later, at the token endpoint, we prove we're
    #   the same client by sending the original code_verifier -- this
    #   replaces the client_secret for public clients like this one.
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = (
        base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        )
        .decode()
        .rstrip("=")  # base64url has no padding in PKCE
    )

    request.session["oauth_state"] = state
    request.session["code_verifier"] = code_verifier

    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid profile email",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(f"{AUTHORIZE_URL}?{query}")


@app.get("/callback")
async def callback(request: Request, code: str, state: str):
    # 1. Check the state matches what we stored in /login
    saved_state = request.session.get("oauth_state")
    if not saved_state or saved_state != state:
        return JSONResponse({"error": "invalid state, possible CSRF"}, status_code=400)

    code_verifier = request.session.get("code_verifier")
    if not code_verifier:
        return JSONResponse({"error": "missing code_verifier, restart login"}, status_code=400)

    # 2. Exchange the authorization code for tokens.
    #    No client_secret here -- code_verifier proves we're the same
    #    client that started the flow (that's what PKCE is for).
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "client_id": CLIENT_ID,
                "code_verifier": code_verifier,
            },
        )

    if token_response.status_code != 200:
        return JSONResponse(
            {"error": "token exchange failed", "details": token_response.text},
            status_code=400,
        )

    tokens = token_response.json()
    id_token = tokens["id_token"]
    print(tokens["access_token"])

    # 3. Verify the ID token's signature using WorkOS's public keys (JWKS)
    async with httpx.AsyncClient() as client:
        jwks = (await client.get(JWKS_URL)).json()

    claims = jwt.decode(
        id_token,
        jwks,
        algorithms=["RS256"],
        audience=CLIENT_ID,
        issuer=AUTHKIT_DOMAIN,
    )

    # 4. Save the verified claims in the session cookie
    request.session["user"] = claims

    return RedirectResponse("/static/protected.html")


@app.get("/api/protected")
def protected(request: Request):
    user = request.session.get("user")
    if not user:
        return JSONResponse({"error": "not logged in"}, status_code=401)
    # This is the "resource server" part: it only serves data because it
    # trusted the ID token claims we verified during /callback.
    return JSONResponse({"message": "This is protected data.", "claims": user})


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/")