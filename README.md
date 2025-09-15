# 📚 Online Library Backend

Backend API for **Online Library System** built with **FastAPI** and **SQLAlchemy**.  
Provides endpoints for managing authors, books, users, and authentication.

---

## 🚀 Features
- User authentication (**JWT-based**)
- Author & Book CRUD operations
- Database integration with SQLAlchemy
- Modular project structure (routers, services, schemas, core)
- Admin-only routes
- Swagger/OpenAPI auto documentation

---

## 📂 Project Structure
```
online-library-backend/
│── app/
│   ├── core/          # config, database, security
│   ├── routers/       # API routes
│   ├── schemas/       # Pydantic models
│   ├── services/      # business logic
│   └── main.py        # FastAPI entrypoint
│
├── migrations/        # Alembic migrations (if added)
├── requirements.txt   # dependencies
└── README.md
```

---

## ⚙️ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/muratowmukam00/online-library-backend.git
   cd online-library-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**  
   Create `.env` file in project root:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/library_db
   SECRET_KEY=your_secret_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. **Run migrations (if Alembic is used)**
   ```bash
   alembic upgrade head
   ```

6. **Run the server**
   ```bash
   uvicorn app.main:app --reload
   ```

---

## 📖 API Documentation
Once the server is running, API docs are available at:
- Swagger UI → `http://127.0.0.1:8000/docs`
- ReDoc → `http://127.0.0.1:8000/redoc`

---

## 🧪 Testing
If you have tests configured:
```bash
pytest
```

---

## 📌 Roadmap
- [ ] Add book borrowing/return endpoints  
- [ ] Add user roles (admin, librarian, reader)  
- [ ] Add Docker & docker-compose support  
- [ ] Improve CI/CD pipeline with GitHub Actions  

---

✍️ Author: **[muratowmukam00](https://github.com/muratowmukam00)**  
