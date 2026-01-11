import redis.asyncio as redis # Use the async version for FastAPI
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    user_ip = request.client.host
    key = f"rate_limit:{user_ip}"
    
    
    request_count = await r.incr(key)
    

    if request_count == 1:
        await r.expire(key, 60)
        
    if request_count > 5:
        return JSONResponse(
            status_code=429, 
            content={"detail": "Too many requests. Try again later."}
        )
        
    return await call_next(request)


@app.get("/data")
async def data():
    return {"message": "ok"}
