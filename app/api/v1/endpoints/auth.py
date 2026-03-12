

# router = APIRouter()

# fake_user = {
#     "email": "admin@test.com",
#     "password": "1234"
# }

# @router.post("/login", response_model=Token)
# def login(user: UserLogin):

#     if user.email != fake_user["email"] or user.password != fake_user["password"]:
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     token = create_access_token({"sub": user.email})

#     return {
#         "access_token": token,
#         "token_type": "bearer"
#     }



from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth_service import register_user, authenticate_user
from app.api.deps import get_db

router = APIRouter()

def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    token = authenticate_user(db, user.email, user.password)

    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "access_token": token,
        "token_type": "bearer",
        "valie user":True
    }


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):

    new_user = register_user(db, user.email, user.password)

    if not new_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # return new_user

    return {
        "id": new_user.id,
        "email": new_user.email,
        "message": "Registration done successfully"
    }