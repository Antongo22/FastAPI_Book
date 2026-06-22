import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SqlAlchemySession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel
from sqlmodel import Session as SQLModelSession


def make_sqlite_override(Base, get_db):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    session_class = SQLModelSession if Base is SQLModel else SqlAlchemySession
    TestingSessionLocal = sessionmaker(bind=engine, class_=session_class, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    return engine, override_get_db


@pytest.fixture
def client_for_app():
    clients = []

    def factory(app):
        client = TestClient(app)
        clients.append(client)
        return client

    yield factory
    for client in clients:
        client.close()
