# Python-FastAPI
Full working version of fast API 


Install requrments 
 pip install fastapi uvicorn python-jose passlib[bcrypt] python-multipart sqlalchemy python-dotenv



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