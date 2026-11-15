import json
import logging
import time
from datetime import datetime, timezone
import httpx
from app.core.config import settings
from app.core.security import sign_webhook_payload
from app.security.ssrf import validate_webhook_url
from app.schemas.notification import WebhookPayload

logger = logging.getLogger("agentconnect.services.webhook")

class WebhookService:
    @staticmethod
    def construct_payload(
        event_id: str,
        post_id: str,
        source_agent_id: str,
        title: str,
        content: str,
        relevance_score: float,
        relevance_explanation: str
    ) -> dict:
        return {
            "event_id": event_id,
            "post_id": post_id,
            "publishing_agent_id": source_agent_id,
            "title": title,
            "content": content,
            "relevance_score": relevance_score,
            "relevance_explanation": relevance_explanation,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    @staticmethod
    async def deliver_webhook(
        webhook_url: str,
        payload_data: dict,
        signing_secret: str = None
    ) -> tuple[bool, int, str]:
        """
        Delivers signed webhook payload over HTTP/HTTPS with SSRF protection.
        Returns: (success: bool, status_code: int, message: str)
        """
        # 1. SSRF Protection check
        is_safe, error_msg = validate_webhook_url(webhook_url)
        if not is_safe:
            logger.warning(f"SSRF Check Rejected webhook to {webhook_url}: {error_msg}")
            return False, 400, f"Blocked by SSRF Guard: {error_msg}"

        # 2. Serialize and sign payload
        json_body = json.dumps(payload_data, separators=(",", ":"))
        signature = sign_webhook_payload(json_body, signing_secret)

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AgentConnect-Webhook-Engine/1.0",
            "X-AgentConnect-Event": "post.matched",
            "X-AgentConnect-Signature": signature,
            "X-AgentConnect-Timestamp": payload_data.get("timestamp", "")
        }

        # 3. Simulated endpoint handling for internal mock agents
        if "agentconnect.internal" in webhook_url or "mock-agent" in webhook_url:
            logger.info(f"Delivered webhook to internal virtual agent endpoint: {webhook_url}")
            return True, 200, "Delivered to internal simulated agent webhook"

        # 4. Outbound HTTP delivery with timeout
        timeout = httpx.Timeout(settings.WEBHOOK_TIMEOUT)
        try:
            async with httpx.AsyncClient(timeout=timeout, verify=False) as client:
                response = await client.post(webhook_url, content=json_body, headers=headers)
                if response.status_code in (200, 201, 202, 204):
                    return True, response.status_code, "Delivered successfully"
                else:
                    return False, response.status_code, f"Target returned status {response.status_code}"
        except httpx.TimeoutException:
            return False, 408, f"Delivery timed out after {settings.WEBHOOK_TIMEOUT} seconds"
        except httpx.RequestError as e:
            return False, 502, f"Network/Connection error: {str(e)}"
        except Exception as e:
            return False, 500, f"Unexpected error during webhook delivery: {str(e)}"
