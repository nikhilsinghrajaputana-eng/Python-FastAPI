# from fastapi import APIRouter, HTTPException
# from app.schemas.user import UserLogin, Token
# from app.core.security import create_access_token

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
from app.schemas.user import UserLogin
from app.services.auth_service import authenticate_user
from app.db.session import SessionLocal

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
        "token_type": "bearer"
    }