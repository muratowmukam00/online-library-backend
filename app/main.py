import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, user, admin_setup, category, author, book, review, favorite, reading_list

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8080",
]

app = FastAPI(
    title="Online Library Backend",
    description="API for a complete online library system.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"msg": "Online  Library API is running"}

app.include_router(admin_setup.router, prefix="/admin-setup" ,tags=["Admin Setup"])

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(user.router, prefix="/users", tags=["Users"])

app.include_router(category.public_router, prefix='/public/categories', tags=["Public Categories"])
app.include_router(author.public_router, prefix="/public/authors", tags=["Public Authors"])
app.include_router(book.public_router, prefix="/public/books", tags=["Public Books"])

app.include_router(category.admin_router, prefix="/admin/categories", tags=["Admin Categories"])
app.include_router(author.admin_router, prefix="/admin/authors", tags=["Admin Authors"])
app.include_router(book.admin_router, prefix="/admin/books", tags=["Admin Books"])

app.include_router(review.router, prefix="/reviews", tags=["review"])
app.include_router(favorite.router, prefix="/favorites", tags=["favorites"])
app.include_router(reading_list.router, prefix="/reading-lists", tags=["reading_lists"])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)