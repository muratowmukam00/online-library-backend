from fastapi import FastAPI
from app.routers import auth, user

app = FastAPI(title="Online Library Backend")

@app.get("/")
def read_root():
    return {"msg": "Online  Library API is running"}

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="/users", tags=["users"])