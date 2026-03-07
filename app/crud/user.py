from sqlalchemy.orm import Session
from app.models.user import User

# def get_user_by_email(db: Session, email: str):

#     return db.query(User).filter(User.email == email).first()


# def create_user(db: Session, email: str, hashed_password: str):

#     user = User(
#         email=email,
#         hashed_password=hashed_password
#     )

#     db.add(user)
#     db.commit()
#     db.refresh(user)

#     return user



# from sqlalchemy.orm import Session
# from app.models.user import User


def get_user_by_email(db: Session, email: str):

    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, email: str, hashed_password: str):

    user = User(
        email=email,
        hashed_password=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user