"""Local Sign in with ChatGPT flow for this open-source, locally hosted app."""
import asyncio
import base64
import hashlib
import json
import logging
import os
import secrets
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx
import jwt
from jwt import PyJWKClient

from backend.config import DATA_DIR

logger = logging.getLogger("dossia.chatgpt_auth")
AUTHORIZATION_ENDPOINT = "https://auth.openai.com/api/accounts/authorize"
TOKEN_ENDPOINT = "https://auth.openai.com/api/accounts/oauth/token"
OPENID_CONFIGURATION = "https://auth.openai.com/.well-known/openid-configuration"
ISSUER = "https://auth.openai.com"
RESOURCE = "https://api.openai.com/v1"
AUTH_FILE = DATA_DIR / "chatgpt_auth.json"
HOST_FILE = DATA_DIR / "chatgpt_host_id"
REQUIRED_SCOPES = {"openid", "email", "profile", "offline_access", "resource.invoke", "chatgpt.tokens.use.direct"}

_pending: Dict[str, Dict[str, str]] = {}
_refresh_lock = asyncio.Lock()
_model_cache: Dict[str, Any] = {"expires_at": 0, "models": []}


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _host_id() -> str:
    if HOST_FILE.exists():
        return HOST_FILE.read_text(encoding="utf-8").strip()
    host_id = f"urn:uuid:{uuid.uuid4()}"
    _write_private(HOST_FILE, host_id)
    return host_id


def _write_private(path: Path, content: str) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix=f"{path.name}-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp_path, 0o600)
        os.replace(temp_path, path)
        os.chmod(path, 0o600)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def _load_credentials() -> Optional[Dict[str, Any]]:
    if not AUTH_FILE.exists():
        return None
    try:
        return json.loads(AUTH_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logger.exception("Could not read local ChatGPT credentials")
        return None


def _save_credentials(credentials: Dict[str, Any]) -> None:
    _write_private(AUTH_FILE, json.dumps(credentials, indent=2))


def connected_status() -> Dict[str, Any]:
    credentials = _load_credentials()
    if not credentials:
        return {"connected": False, "plan_usage_enabled": False, "email": None}
    scopes = set(credentials.get("scopes", []))
    return {
        "connected": bool(credentials.get("refresh_token") and credentials.get("access_token")),
        "plan_usage_enabled": bool(credentials.get("refresh_token")) and "chatgpt.tokens.use.direct" in scopes,
        "email": credentials.get("email"),
        "expires_at": credentials.get("expires_at"),
    }


def create_authorization_url(callback_uri: str) -> str:
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    verifier = _b64url(secrets.token_bytes(32))
    challenge = _b64url(hashlib.sha256(verifier.encode("ascii")).digest())
    existing = _load_credentials() or {}
    registered_client_id = existing.get("client_id")
    client_id = registered_client_id or "dynamic_agent_client"
    _pending[state] = {
        "nonce": nonce,
        "verifier": verifier,
        "redirect_uri": callback_uri,
        "expected_client_id": registered_client_id or "",
        "expected_subject": existing.get("subject", "") if registered_client_id else "",
    }
    # Keep a bounded number of abandoned browser attempts in process memory.
    if len(_pending) > 20:
        _pending.pop(next(iter(_pending)))

    query = {
        "client_id": client_id,
        "ext_agent_host_id": _host_id(),
        "response_type": "code",
        "redirect_uri": callback_uri,
        "scope": "openid profile email offline_access resource.invoke chatgpt.tokens.use.direct",
        "resource": RESOURCE,
        "state": state,
        "nonce": nonce,
        "code_challenge_method": "S256",
        "code_challenge": challenge,
    }
    if not registered_client_id:
        query["agent_name_hint"] = "Dossia"
    elif existing.get("id_token"):
        query["id_token_hint"] = existing["id_token"]
        if existing.get("email"):
            query["login_hint"] = existing["email"]
    return f"{AUTHORIZATION_ENDPOINT}?{urlencode(query)}"


def cancel_authorization(state: str) -> None:
    _pending.pop(state, None)


async def finish_authorization(code: str, state: str, issued_client_id: str) -> Dict[str, Any]:
    attempt = _pending.pop(state, None)
    if not attempt:
        raise ValueError("This sign-in attempt expired or its state did not match. Start again from Dossia.")
    expected_client_id = attempt.get("expected_client_id")
    if expected_client_id:
        if issued_client_id and issued_client_id != expected_client_id:
            raise ValueError("OpenAI returned a different account registration. Start sign-in again.")
        issued_client_id = expected_client_id
    if not code or not issued_client_id or issued_client_id == "dynamic_agent_client":
        raise ValueError("OpenAI did not return a completed client registration. Start sign-in again.")

    if not expected_client_id:
        # Preserve the issued registration even if the one-time code expires before exchange.
        _save_credentials({"client_id": issued_client_id, "ext_agent_host_id": _host_id()})

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(TOKEN_ENDPOINT, data={
            "grant_type": "authorization_code",
            "client_id": issued_client_id,
            "code": code,
            "code_verifier": attempt["verifier"],
            "redirect_uri": attempt["redirect_uri"],
            "resource": RESOURCE,
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    if response.is_error:
        logger.warning("ChatGPT OAuth token exchange failed with HTTP %s", response.status_code)
        raise ValueError("OpenAI could not finish sign-in. Start a fresh connection from Dossia.")
    token_data = response.json()
    granted_scopes = set((token_data.get("scope") or "").split())
    if not REQUIRED_SCOPES.issubset(granted_scopes):
        raise ValueError("ChatGPT plan usage was not authorized. Reconnect and allow Dossia to use your plan.")

    id_token = token_data.get("id_token")
    if not id_token:
        raise ValueError("OpenAI did not return an identity token; sign-in could not be verified.")
    async with httpx.AsyncClient(timeout=15.0) as client:
        discovery = await client.get(OPENID_CONFIGURATION)
        discovery.raise_for_status()
        oidc = discovery.json()
    signing_key = PyJWKClient(oidc["jwks_uri"], timeout=15).get_signing_key_from_jwt(id_token)
    identity = jwt.decode(
        id_token,
        signing_key.key,
        algorithms=["RS256"],
        audience=issued_client_id,
        issuer=ISSUER,
        options={"require": ["exp", "iat", "sub"]},
        leeway=60,
    )
    if identity.get("nonce") != attempt["nonce"]:
        raise ValueError("The sign-in response could not be verified. Start a new connection.")
    if attempt.get("expected_subject") and identity.get("sub") != attempt["expected_subject"]:
        raise ValueError("This sign-in belongs to a different ChatGPT account. Start again and choose the connected account.")

    now = int(time.time())
    credentials = {
        "email": identity.get("email"),
        "subject": identity["sub"],
        "issuer": ISSUER,
        "client_id": issued_client_id,
        "ext_agent_host_id": _host_id(),
        "id_token": id_token,
        "access_token": token_data["access_token"],
        "refresh_token": token_data["refresh_token"],
        "token_type": token_data.get("token_type", "Bearer"),
        "expires_at": now + int(token_data.get("expires_in", 3600)),
        "scopes": sorted(granted_scopes),
    }
    _save_credentials(credentials)
    _model_cache.update(expires_at=0, models=[])
    return connected_status()


async def access_token() -> str:
    async with _refresh_lock:
        credentials = _load_credentials()
        if not credentials or not credentials.get("refresh_token") or "chatgpt.tokens.use.direct" not in credentials.get("scopes", []):
            raise RuntimeError("Connect ChatGPT in Dossia Settings and allow ChatGPT plan usage first.")
        if credentials.get("expires_at", 0) > int(time.time()) + 90:
            return credentials["access_token"]

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(TOKEN_ENDPOINT, data={
                "grant_type": "refresh_token",
                "client_id": credentials["client_id"],
                "refresh_token": credentials["refresh_token"],
                "resource": RESOURCE,
            }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        if response.is_error:
            logger.warning("ChatGPT OAuth refresh failed with HTTP %s", response.status_code)
            raise RuntimeError("Your ChatGPT connection expired or was revoked. Reconnect it in Dossia Settings.")
        token_data = response.json()
        credentials.update({
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token", credentials["refresh_token"]),
            "expires_at": int(time.time()) + int(token_data.get("expires_in", 3600)),
            "scopes": sorted(set((token_data.get("scope") or " ".join(credentials["scopes"])).split())),
        })
        if "chatgpt.tokens.use.direct" not in credentials["scopes"]:
            raise RuntimeError("ChatGPT plan permission was removed. Reconnect ChatGPT in Dossia Settings.")
        _save_credentials(credentials)
        return credentials["access_token"]


async def available_models() -> list:
    now = time.time()
    if _model_cache["expires_at"] > now:
        return _model_cache["models"]
    token = await access_token()
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{RESOURCE}/models", headers={"Authorization": f"Bearer {token}"})
    if response.is_error:
        raise RuntimeError("Could not load the models available to this ChatGPT account.")
    data = response.json()
    models = [{"id": model.get("slug"), "name": model.get("display_name") or model.get("slug")}
              for model in data.get("models", [])
              if model.get("visibility") == "list" and model.get("slug")]
    _model_cache.update(expires_at=now + 300, models=models)
    return models


async def revoke_and_disconnect() -> None:
    credentials = _load_credentials()
    if not credentials:
        return
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            discovery = await client.get(OPENID_CONFIGURATION)
            discovery.raise_for_status()
            revocation_endpoint = discovery.json()["revocation_endpoint"]
            response = await client.post(revocation_endpoint, data={
                "token": credentials.get("refresh_token", ""),
                "token_type_hint": "refresh_token",
                "client_id": credentials["client_id"],
            }, headers={"Content-Type": "application/x-www-form-urlencoded"})
            response.raise_for_status()
    except httpx.HTTPError:
        logger.warning("Could not confirm remote ChatGPT session revocation; clearing local credentials")
    for token_field in ("access_token", "refresh_token", "expires_at", "scopes"):
        credentials.pop(token_field, None)
    _save_credentials(credentials)
    _model_cache.update(expires_at=0, models=[])
