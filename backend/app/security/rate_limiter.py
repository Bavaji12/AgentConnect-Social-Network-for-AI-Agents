import time
from collections import defaultdict
from fastapi import Request, HTTPException, status
from app.core.config import settings

class InMemoryRateLimiter:
    def __init__(self, requests_per_minute: int = 120):
        self.rate_limit = requests_per_minute
        self.requests = defaultdict(list)

    def check_rate_limit(self, client_id: str) -> bool:
        current_time = time.time()
        window_start = current_time - 60.0

        # Purge timestamps older than 1 minute
        self.requests[client_id] = [
            t for t in self.requests[client_id] if t > window_start
        ]

        if len(self.requests[client_id]) >= self.rate_limit:
            return False

        self.requests[client_id].append(current_time)
        return True

rate_limiter = InMemoryRateLimiter(settings.RATE_LIMIT_PER_MINUTE)

async def rate_limit_dependency(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    # Also check Authorization header or API key for per-agent rate limit
    auth_header = request.headers.get("Authorization", "")
    identifier = auth_header if auth_header else client_ip

    if not rate_limiter.check_rate_limit(identifier):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please retry after a few moments."
        )
