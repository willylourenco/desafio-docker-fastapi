import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app, Base, get_db


SQLALCHEMY_DATABASE_URL = "sqlite://" 

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)



def test_read_main():
    
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API de Produtos está no ar!"}

def test_create_produto():
    
    response = client.post(
        "/produtos/",
        json={"nome": "Mouse Gamer", "descricao": "DPI Ajustável"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Mouse Gamer"
    assert data["descricao"] == "DPI Ajustável"
    assert "id" in data

def test_read_produtos():
  
    client.post("/produtos/", json={"nome": "Teclado", "descricao": "Mecânico"})
    
  
    response = client.get("/produtos/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["nome"] == "Teclado"