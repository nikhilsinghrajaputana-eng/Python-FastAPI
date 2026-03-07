from sqlalchemy.orm import Session
from app.crud.user import get_user_by_email,create_user
from app.core.security import verify_password, create_access_token
from app.core.security import hash_password


def authenticate_user(db: Session, email: str, password: str):

    user = get_user_by_email(db, email)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    token = create_access_token({"sub": user.email})

    return token



def register_user(db: Session, email: str, password: str):

    existing_user = get_user_by_email(db, email)

    if existing_user:
        return None

    hashed_password = hash_password(password)

    user = create_user(db, email, hashed_password)

    return user