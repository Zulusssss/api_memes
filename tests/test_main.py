from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
import pytest
import base64

# Создаем тестовую базу данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Переопределяем зависимость get_db для использования тестовой базы данных
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Создаем все таблицы в тестовой базе данных
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

# Пример изображения в формате base64
image_data = base64.b64encode(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01\xe2!\xbc\x33\x00\x00\x00\x00IEND\xaeB`\x82').decode('utf-8')

test_meme_data = {
    "title": "Test Meme",
    "description": "Test Description",
    "image_data": image_data
}

@pytest.fixture(scope="module")
def get_token():
    # Регистрируем нового пользователя
    client.post("/api/v1/auth/register", json={"username": "user", "password": "password"})
    # Получаем токен для этого пользователя
    response = client.post("/api/v1/auth/token", json={"username": "user", "password": "password"})
    assert response.status_code == 200
    return response.json()["access_token"]

def test_create_meme(get_token):
    token = get_token
    response = client.post(
        "/api/v1/media/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Test Meme", "description": "Test Description", "image_data": test_meme_data["image_data"]}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Meme"

def test_read_memes():
    response = client.get("/api/v1/memes/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_meme(get_token):
    token = get_token
    response = client.post(
        "/api/v1/media/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Test Meme", "description": "Test Description", "image_data": test_meme_data["image_data"]}
    )
    meme_id = response.json()["id"]

    response = client.get(f"/api/v1/memes/{meme_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Meme"

def test_update_meme(get_token):
    token = get_token
    response = client.post(
        "/api/v1/media/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Test Meme", "description": "Test Description", "image_data": test_meme_data["image_data"]}
    )
    meme_id = response.json()["id"]

    updated_image_data = base64.b64encode(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01\xe2!\xbc\x33\x00\x00\x00\x00IEND\xaeB`\x82').decode('utf-8')
    updated_data = {
        "title": "Updated Meme",
        "description": "Updated Description",
        "image_data": updated_image_data
    }
    response = client.put(
        f"/api/v1/media/{meme_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": updated_data["title"], "description": updated_data["description"], "image_data": updated_data["image_data"]}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Meme"

def test_delete_meme(get_token):
    token = get_token
    response = client.post(
        "/api/v1/media/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Test Meme", "description": "Test Description", "image_data": test_meme_data["image_data"]}
    )
    meme_id = response.json()["id"]

    response = client.delete(
        f"/api/v1/media/{meme_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    response = client.get(f"/api/v1/memes/{meme_id}")
    assert response.status_code == 404
