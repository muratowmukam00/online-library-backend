from fastapi import FastAPI
from app.routers import auth, user, admin_setup

app = FastAPI(title="Online Library Backend")

@app.get("/")
def read_root():
    return {"msg": "Online  Library API is running"}

app.include_router(admin_setup.router, prefix="/admin-setup" ,tags=["admin_setup"])

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="/users", tags=["users"])