import redis.asyncio as redis
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError
from policies import adjust_limit

# Configuration
BASE_RATE_LIMIT = 5  # requests per minute
WINDOW_SIZE = 60     # seconds

app = FastAPI()

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    user_ip = request.client.host
    key = f"rate_limit:{user_ip}"
    
    try:
        # Use pipeline for atomic operations
        pipe = r.pipeline()
        pipe.incr(key)
        pipe.expire(key, WINDOW_SIZE)
        request_count = (await pipe.execute())[0]
            
        limit = adjust_limit(BASE_RATE_LIMIT)

        if request_count > limit:
            return JSONResponse(
                status_code=429, 
                content={"detail": "Too many requests. Try again later."}
            )
    except RedisError:
        # If Redis is down, allow the request but log the error
        print(f"Redis error for {user_ip}, allowing request")
        # In production, you might want to use a fallback limiter here
        
    # Continue with the request
    response = await call_next(request)
    
    # Add rate limit headers
    try:
        limit = adjust_limit(BASE_RATE_LIMIT)
        remaining = max(0, limit - request_count)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(WINDOW_SIZE)
    except:
        pass  # If we couldn't get rate limit info, skip headers
    
    return response


@app.get("/data")
async def data():
    return {"message": "ok"}


@app.get("/health")
async def health_check():
    try:
        await r.ping()
        return {
            "status": "healthy",
            "redis": "connected",
            "rate_limiter": "active"
        }
    except RedisError:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "redis": "disconnected",
                "rate_limiter": "degraded"
            }
        )
    