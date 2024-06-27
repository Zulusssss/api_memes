from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.deps import get_db, get_current_user
from app.s3_client import s3_client
import base64
import uuid

router = APIRouter()

@router.post("/", response_model=schemas.Meme, status_code=201)
def create_meme(
    meme: schemas.MemeCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    image_data = base64.b64decode(meme.image_data.encode('utf-8'))
    file_name = f"{uuid.uuid4()}.png"
    s3_client.upload_bytes(image_data, file_name)

    meme_create = schemas.MemeCreate(title=meme.title, description=meme.description, image_data=meme.image_data)
    created_meme = crud.create_meme(db=db, meme=meme_create)

    # Сохраняем имя файла в БД
    created_meme.file_name = file_name
    db.commit()
    db.refresh(created_meme)

    return created_meme

@router.put("/{meme_id}", response_model=schemas.Meme)
def update_meme(
    meme_id: int,
    meme: schemas.MemeUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    db_meme = crud.get_meme(db, meme_id)
    if db_meme is None:
        raise HTTPException(status_code=404, detail="Meme not found")

    # Удаляем старую картинку из MinIO
    if db_meme.file_name:
        s3_client.delete_file(db_meme.file_name)

    # Загружаем новую картинку
    image_data = base64.b64decode(meme.image_data.encode('utf-8'))
    new_file_name = f"{uuid.uuid4()}.png"
    s3_client.upload_bytes(image_data, new_file_name)

    meme_update = schemas.MemeUpdate(title=meme.title, description=meme.description, image_data=meme.image_data)
    updated_meme = crud.update_meme(db=db, meme_id=meme_id, meme=meme_update)

    # Сохраняем имя нового файла в БД
    updated_meme.file_name = new_file_name
    db.commit()
    db.refresh(updated_meme)

    return updated_meme

@router.delete("/{meme_id}", response_model=schemas.Meme)
def delete_meme(
    meme_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    db_meme = crud.get_meme(db, meme_id)
    if db_meme is None:
        raise HTTPException(status_code=404, detail="Meme not found")

    # Удаляем картинку из MinIO
    if db_meme.file_name:
        s3_client.delete_file(db_meme.file_name)

    return crud.delete_meme(db=db, meme_id=meme_id)
