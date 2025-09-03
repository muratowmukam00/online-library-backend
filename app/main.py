from fastapi import FastAPI

app = FastAPI(title="Online Library Backend")

@app.get("/")
def read_root():
    return {"msg": "Online  Library API is running"}