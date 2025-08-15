import httpx
from typing import Optional, Dict, Any

from app.core.config import settings


class TelegramService:
    def __init__(self, bot_token: Optional[str] = None) -> None:
        self.bot_token = bot_token or settings.TELEGRAM_BOT_TOKEN

    async def send_message(self, chat_id: int, text: str, reply_markup: Optional[Dict[str, Any]] = None) -> None:
        if not self.bot_token:
            raise RuntimeError("Telegram bot token is not configured")
        api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": text,
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(api_url, json=payload)
            if resp.status_code != 200 and reply_markup:
                # Фолбэк: конвертируем web_app кнопку в обычный URL, если возможно
                fallback = _webapp_to_url_fallback(reply_markup)
                if fallback:
                    await client.post(api_url, json={
                        "chat_id": chat_id,
                        "text": text,
                        "reply_markup": fallback
                    })


def _webapp_to_url_fallback(reply_markup: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        ik = reply_markup.get("inline_keyboard")
        if not ik:
            return None
        fallback_rows = []
        for row in ik:
            new_row = []
            for btn in row:
                if "web_app" in btn and isinstance(btn["web_app"], dict) and "url" in btn["web_app"]:
                    new_row.append({"text": btn.get("text", "Открыть"), "url": btn["web_app"]["url"]})
                else:
                    new_row.append(btn)
            fallback_rows.append(new_row)
        return {"inline_keyboard": fallback_rows}
    except Exception:
        return None


