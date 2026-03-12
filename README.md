# Python-FastAPI
Full working version of fast API 


Install requrments 
 pip install fastapi uvicorn python-jose passlib[bcrypt] python-multipart sqlalchemy python-dotenv

<pre >

fastapi-backend/
│
├── app/
│   ├── main.py
│   │
│   ├── core/                # global configs
│   │   ├── config.py
│   │   ├── security.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │
│   ├── models/              # database models
│   │   └── user.py
│   │
│   ├── schemas/             # request/response schemas
│   │   └── user.py
│   │
│   ├── crud/                # database queries
│   │   └── user.py
│   │
│   ├── api/                 # API routes
│   │   └── v1/
│   │        ├── router.py
│   │        └── endpoints/
│   │             └── auth.py
│   │
│   └── services/            # business logic
│        └── auth_service.py
│
├── requirements.txt
└── .env

</pre>

# Data Base :
    PG Admin
# Main libraries 
FastAPI

Uvicorn

SQLAlchemy

python-jose
pip install sqlalchemy psycopg2-binary alembic


python -m uvicorn app.main:app --reload




INSERT INTO users (email, hashed_password)
VALUES (
'admin@test.com',
'$2b$12$ZJaOHea2qInbekbZ0E5YIeP7jD31GWQ8uDV/5/3zrAeCSUX/exqIC'
);

ram123@
