# generate_pkce.py
import base64, hashlib, secrets

# Generate a random verifier
code_verifier = secrets.token_urlsafe(64)
print(f"CODE_VERIFIER: {code_verifier}")

# Create the challenge
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode()).digest()
).decode().rstrip("=")
print(f"CODE_CHALLENGE: {code_challenge}")