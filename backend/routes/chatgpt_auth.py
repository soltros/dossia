from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx
import ipaddress
from fastapi import Request

from backend import chatgpt_auth

router = APIRouter(prefix="/api/chatgpt-auth", tags=["chatgpt-auth"])


@router.get("/start")
async def start_chatgpt_sign_in(request: Request):
    peer = request.client.host if request.client else ""
    try:
        if not ipaddress.ip_address(peer).is_loopback:
            raise HTTPException(status_code=403, detail="ChatGPT sign-in is only available from this computer")
    except ValueError:
        raise HTTPException(status_code=403, detail="ChatGPT sign-in is only available from this computer")
    port = request.url.port or 8000
    callback_uri = f"http://127.0.0.1:{port}/api/chatgpt-auth/callback"
    return RedirectResponse(chatgpt_auth.create_authorization_url(callback_uri), status_code=302)


@router.get("/callback", response_class=HTMLResponse)
async def chatgpt_sign_in_callback(
    request: Request,
    code: str = Query(""),
    state: str = Query(""),
    client_id: str = Query(""),
    error: str = Query(""),
):
    if error:
        if state:
            chatgpt_auth.cancel_authorization(state)
        message = "Sign-in was canceled. You can close this window and try again."
    else:
        try:
            await chatgpt_auth.finish_authorization(code, state, client_id)
            message = "ChatGPT is connected. You can close this window and return to Dossia."
        except (ValueError, httpx.HTTPError) as exc:
            message = str(exc)
        except Exception:
            message = "Dossia could not verify the ChatGPT sign-in. Return to Dossia Settings and try again."
    port = request.url.port or 8000
    return HTMLResponse(f"""<!doctype html><html><head><meta charset="utf-8"><title>Dossia ChatGPT sign-in</title></head>
<body><main><h1>{_escape(message)}</h1><p>This window can be closed.</p><p><a href="http://127.0.0.1:{port}/">Return to Dossia</a></p></main>
<script>if (window.opener) {{ window.opener.postMessage({{type:'dossia-chatgpt-auth'}}, '*'); window.close(); }}</script></body></html>""")


def _escape(value: str) -> str:
    import html
    return html.escape(value, quote=True)


@router.get("/status")
async def chatgpt_connection_status():
    return chatgpt_auth.connected_status()


@router.get("/models")
async def chatgpt_models():
    try:
        return {"models": await chatgpt_auth.available_models()}
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Could not load models from OpenAI. Check your connection and retry.")


@router.post("/disconnect")
async def disconnect_chatgpt():
    await chatgpt_auth.revoke_and_disconnect()
    return {"status": "disconnected"}
