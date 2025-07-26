import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models import db, User, Category
from config import TestingConfig
@pytest.fixture(autouse=True)
def patch_async_notify(monkeypatch):
    monkeypatch.setattr('utils.notify_util.send_email_notify_order_created', lambda *a, **k: None)
    monkeypatch.setattr('utils.notify_util.send_line_notify_order_created', lambda *a, **k: None)

@pytest.fixture
def app():
    db_name = os.environ.get('TEST_DB_NAME', 'Ecommerce_test')
    db_uri = f'postgresql://postgres:talen168168@localhost:5432/{db_name}'

    app = create_app(config_name="testing", test_config={
    'SQLALCHEMY_DATABASE_URI': db_uri,
    'TESTING': True,
    'JWT_SECRET_KEY': 'testkey',
})  
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
