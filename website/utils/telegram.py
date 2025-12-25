import json
import urllib.parse
import urllib.request
from django.conf import settings
import os


def _get_active_recipients():
    """Return list of (token, chat_id) from active DB recipients, or empty list if none/Model missing."""
    try:
        from administrator.models import TelegramRecipient  # local import to avoid circulars
        recipients = list(
            TelegramRecipient.objects.filter(aktif=True).values_list("bot_token", "chat_id")
        )
        # filter out incomplete pairs
        return [(t, c) for t, c in recipients if t and c]
    except Exception:
        return []


def _send_message_once(text: str, token: str, chat_id: str) -> dict:
    base_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(base_url, data=data)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            status = resp.getcode()
            body = resp.read()
            try:
                decoded = json.loads(body.decode("utf-8"))
            except Exception:
                decoded = {"raw": body.decode("utf-8", errors="ignore")}
            ok = status == 200
            if ok and isinstance(decoded, dict) and decoded.get("ok") is False:
                ok = False
            return {"success": ok, "status": status, "message": "OK" if ok else str(decoded)}
    except Exception as e:
        return {"success": False, "status": None, "message": str(e)}


def send_telegram_message(text: str, token: str | None = None, chat_id: str | None = None) -> dict:
    """
    Send a text message to a Telegram chat.

    Falls back to settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID
    when token/chat_id are not provided. Returns dict with keys:
    {success: bool, status: int|None, message: str}
    """
    # If explicit token/chat_id provided, send once using those.
    if token and chat_id:
        return _send_message_once(text, token, chat_id)

    # Try DB-managed recipients first.
    recipients = _get_active_recipients()
    if recipients:
        results = []
        any_ok = False
        for t, c in recipients:
            r = _send_message_once(text, t, c)
            results.append(r)
            any_ok = any_ok or r.get("success")
        return {"success": any_ok, "status": None, "message": results}

    # Fallback to settings when DB has no active recipients.
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    chat_id = getattr(settings, "TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return {"success": False, "status": None, "message": "Missing token/chat_id. Set in admin (TelegramRecipient) or settings/env."}
    return _send_message_once(text, token, chat_id)


def _ensure_requests():
    try:
        import requests  # noqa: F401
        return True, None
    except Exception as e:
        return False, f"Python 'requests' not available: {e}. Install with: pip install requests"


def send_telegram_document(file_path: str, caption: str = "", token: str | None = None, chat_id: str | None = None) -> dict:
    """Upload and send a local file as document to Telegram (works without public URL).
    Uses 'requests' for multipart upload. Returns dict like send_telegram_message.
    """
    # If explicit token/chat_id provided, send once using those.
    if token and chat_id:
        single = True
        pairs = [(token, chat_id)]
    else:
        # DB recipients first
        recipients = _get_active_recipients()
        if recipients:
            single = False
            pairs = recipients
        else:
            # Fallback settings
            t = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
            c = getattr(settings, "TELEGRAM_CHAT_ID", "")
            if not t or not c:
                return {"success": False, "status": None, "message": "Missing token/chat_id"}
            single = True
            pairs = [(t, c)]
    if not os.path.isfile(file_path):
        return {"success": False, "status": None, "message": f"File not found: {file_path}"}
    ok, msg = _ensure_requests()
    if not ok:
        return {"success": False, "status": None, "message": msg}
    import requests
    results = []
    any_ok = False
    for t, c in pairs:
        url = f"https://api.telegram.org/bot{t}/sendDocument"
        try:
            with open(file_path, "rb") as f:
                resp = requests.post(url, data={"chat_id": c, "caption": caption}, files={"document": f}, timeout=30)
            j = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"text": resp.text}
            ok_resp = resp.ok and j.get("ok", True)
            any_ok = any_ok or ok_resp
            results.append({"success": ok_resp, "status": resp.status_code, "message": "OK" if ok_resp else str(j)})
        except Exception as e:
            results.append({"success": False, "status": None, "message": str(e)})
    return {"success": any_ok, "status": None, "message": results}


def send_telegram_photo(file_path: str, caption: str = "", token: str | None = None, chat_id: str | None = None) -> dict:
    """Upload and send a local image as photo to Telegram (multipart)."""
    if token and chat_id:
        single = True
        pairs = [(token, chat_id)]
    else:
        recipients = _get_active_recipients()
        if recipients:
            single = False
            pairs = recipients
        else:
            t = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
            c = getattr(settings, "TELEGRAM_CHAT_ID", "")
            if not t or not c:
                return {"success": False, "status": None, "message": "Missing token/chat_id"}
            single = True
            pairs = [(t, c)]
    if not os.path.isfile(file_path):
        return {"success": False, "status": None, "message": f"File not found: {file_path}"}
    ok, msg = _ensure_requests()
    if not ok:
        return {"success": False, "status": None, "message": msg}
    import requests
    results = []
    any_ok = False
    for t, c in pairs:
        url = f"https://api.telegram.org/bot{t}/sendPhoto"
        try:
            with open(file_path, "rb") as f:
                resp = requests.post(url, data={"chat_id": c, "caption": caption}, files={"photo": f}, timeout=30)
            j = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"text": resp.text}
            ok_resp = resp.ok and j.get("ok", True)
            any_ok = any_ok or ok_resp
            results.append({"success": ok_resp, "status": resp.status_code, "message": "OK" if ok_resp else str(j)})
        except Exception as e:
            results.append({"success": False, "status": None, "message": str(e)})
    return {"success": any_ok, "status": None, "message": results}


def send_telegram_document_url(file_url: str, caption: str = "", token: str | None = None, chat_id: str | None = None) -> dict:
    """Send a document by URL (Telegram will fetch it). Requires the URL to be publicly accessible."""
    if token and chat_id:
        pairs = [(token, chat_id)]
    else:
        recipients = _get_active_recipients()
        if recipients:
            pairs = recipients
        else:
            t = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
            c = getattr(settings, "TELEGRAM_CHAT_ID", "")
            if not t or not c:
                return {"success": False, "status": None, "message": "Missing token/chat_id"}
            pairs = [(t, c)]
    results = []
    any_ok = False
    for t, c in pairs:
        base_url = f"https://api.telegram.org/bot{t}/sendDocument"
        payload = {"chat_id": c, "document": file_url, "caption": caption}
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(base_url, data=data)
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                status = resp.getcode()
                body = resp.read().decode("utf-8", errors="ignore")
                try:
                    decoded = json.loads(body)
                except Exception:
                    decoded = {"raw": body}
                ok = status == 200 and (not isinstance(decoded, dict) or decoded.get("ok", True))
                any_ok = any_ok or ok
                results.append({"success": ok, "status": status, "message": "OK" if ok else str(decoded)})
        except Exception as e:
            results.append({"success": False, "status": None, "message": str(e)})
    return {"success": any_ok, "status": None, "message": results}
