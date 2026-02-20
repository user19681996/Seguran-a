import time, threading
from collections import defaultdict, deque
from typing import Tuple
from app.core.config import RATE_LIMIT_PER_MINUTE, RATE_LIMIT_BURST

_lock = threading.Lock()
_hits = defaultdict(lambda: deque())

def check_rate_limit(key: str) -> Tuple[bool, int]:
    now = time.time()
    window = 60.0
    with _lock:
        q = _hits[key]
        while q and q[0] < now - window:
            q.popleft()
        limit = RATE_LIMIT_PER_MINUTE + RATE_LIMIT_BURST
        if len(q) >= limit:
            retry_after = int((q[0] + window) - now) + 1
            return False, max(retry_after, 1)
        q.append(now)
        return True, 0
