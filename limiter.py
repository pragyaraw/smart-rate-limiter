import time
import asyncio
from collections import defaultdict


request_log = defaultdict(lambda: defaultdict(int))
lock = asyncio.Lock()

async def allow_request(user, limit):
    current_minute = int(time.time() // 60)
    
    async with lock:
        for logged_minute in list(request_log.keys()):
            if logged_minute < current_minute:
                del request_log[logged_minute]
        
        
        request_log[current_minute][user] += 1
        
        
        current_count = request_log[current_minute][user]
        
        return current_count <= limit