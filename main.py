from fastapi import FastAPI
from webhook import webhook_router

app = FastAPI()
app.include_router(webhook_router)

@app.get("/")
async def root():
    return {"message": "Bot is running"}