import os
import time  # <--- Importamos a biblioteca 'time'
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

# 1. Configuração do Banco de Dados (lendo de variáveis de ambiente)
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "appdb")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# 2. Configuração do SQLAlchemy (Agora são 'None' e serão iniciados no startup)
engine: Engine | None = None
SessionLocal: sessionmaker | None = None
Base = declarative_base()  # Definimos a Base aqui

# 3. Definição do Modelo (Tabela do Banco)
class Produto(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    descricao = Column(String)

# 4. Definição dos Schemas (Pydantic)
class ProdutoBase(BaseModel):
    nome: str
    descricao: str | None = None

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoSchema(ProdutoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# 5. Inicialização do FastAPI
app = FastAPI()

# 6. FUNÇÃO DE STARTUP (MODIFICADA COM RETRY)
# Esta função agora vai tentar se conectar ao banco 10x
# antes de desistir.
@app.on_event("startup")
def on_startup():
    global engine, SessionLocal
    
    max_retries = 10
    retries = 0
    
    while retries < max_retries:
        try:
            print(f"Tentando conectar ao banco de dados... (Tentativa {retries + 1})")
            
            # Tenta criar a 'engine'
            engine = create_engine(DATABASE_URL)
            
            # Tenta se conectar de fato
            with engine.connect() as conn:
                print("Conexão estabelecida com sucesso.")
            
            # Tenta criar a 'SessionLocal'
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            
            # Tenta criar as tabelas
            print("Tentando criar tabelas...")
            Base.metadata.create_all(bind=engine)
            print("Tabelas criadas com sucesso (ou já existentes).")
            
            # Se tudo deu certo, sai do loop
            break 
        
        except Exception as e:
            print(f"Erro ao conectar ou criar tabelas: {e}")
            retries += 1
            print(f"Aguardando 3 segundos antes da próxima tentativa...")
            time.sleep(3) # Espera 3 segundos

    if SessionLocal is None or engine is None:
        print("NÃO FOI POSSÍVEL CONECTAR AO BANCO DE DADOS APÓS VÁRIAS TENTATIVAS.")
        # Isso fará a aplicação falhar se não conseguir conectar
        raise Exception("Falha ao inicializar o banco de dados")

# 7. Dependência para obter a sessão do DB
@contextmanager
def get_db_session():
    if SessionLocal is None:
        raise HTTPException(status_code=503, detail="Serviço indisponível: Conexão com o banco falhou na inicialização")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Wrapper de dependência para o FastAPI
def get_db():
    with get_db_session() as db:
        yield db

# 8. Endpoints do CRUD (sem alteração)
@app.get("/")
def read_root():
    return {"message": "API de Produtos está no ar!"}

@app.post("/produtos/", response_model=ProdutoSchema)
def create_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    db_produto = Produto(nome=produto.nome, descricao=produto.descricao)
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto

@app.get("/produtos/", response_model=list[ProdutoSchema])
def read_produtos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    produtos = db.query(Produto).offset(skip).limit(limit).all()
    return produtos

@app.get("/produtos/{produto_id}", response_model=ProdutoSchema)
def read_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto