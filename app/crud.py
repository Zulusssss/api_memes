from sqlalchemy.orm import Session
from app.models import User, Meme, Token
from app.schemas import UserCreate, MemeCreate, MemeUpdate
from app.security import get_password_hash

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_token(db: Session, token: str, user_id: int):
    db_token = Token(token=token, owner_id=user_id)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def get_user_by_token(db: Session, token: str):
    return db.query(User).join(Token).filter(Token.token == token).first()

def get_meme(db: Session, meme_id: int):
    return db.query(Meme).filter(Meme.id == meme_id).first()

def get_memes(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Meme).offset(skip).limit(limit).all()

def create_meme(db: Session, meme: MemeCreate):
    db_meme = Meme(**meme.dict())
    db.add(db_meme)
    db.commit()
    db.refresh(db_meme)
    return db_meme

def update_meme(db: Session, meme_id: int, meme: MemeUpdate):
    db_meme = get_meme(db, meme_id)
    if db_meme:
        for key, value in meme.dict().items():
            setattr(db_meme, key, value)
        db.commit()
        db.refresh(db_meme)
    return db_meme

def delete_meme(db: Session, meme_id: int):
    db_meme = get_meme(db, meme_id)
    if db_meme:
        db.delete(db_meme)
        db.commit()
    return db_meme
