import asyncio
import json
import logging
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger("agentconnect.workers.queue")

class WorkerEventQueue:
    """
    Unified asynchronous event queue.
    Uses Redis when available, with automatic in-memory asyncio fallback for local/test runs.
    """
    def __init__(self):
        self._redis = None
        self._memory_queue: asyncio.Queue = asyncio.Queue()
        self._connected = False

    async def connect(self):
        try:
            import redis.asyncio as aioredis
            client = aioredis.from_url(settings.REDIS_URL, socket_timeout=1.0)
            await client.ping()
            self._redis = client
            self._connected = True
            logger.info(f"Connected to Redis at {settings.REDIS_URL}")
        except Exception as e:
            logger.info(f"Redis not available ({e}). Using in-memory asynchronous worker queue.")
            self._connected = False

    async def enqueue(self, task_name: str, payload: Dict[str, Any]):
        message = json.dumps({"task": task_name, "payload": payload})
        if self._connected and self._redis:
            try:
                await self._redis.rpush("agentconnect:jobs", message)
                return
            except Exception as e:
                logger.warning(f"Redis rpush failed: {e}. Falling back to in-memory queue.")
        
        await self._memory_queue.put(message)

    async def dequeue(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        if self._connected and self._redis:
            try:
                item = await self._redis.blpop("agentconnect:jobs", timeout=int(timeout))
                if item:
                    return json.loads(item[1])
            except Exception:
                pass

        try:
            item = await asyncio.wait_for(self._memory_queue.get(), timeout=timeout)
            return json.loads(item)
        except (asyncio.TimeoutError, Exception):
            return None

event_queue = WorkerEventQueue()
