from fastapi import FastAPI
from webhook import router as telegram_router

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Crypto Groq Bot is live"}

app.include_router(telegram_router, prefix="")