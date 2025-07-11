import pytest
import sys
import os
#最優先去指定的資料(專案根目錄下) 來imprt程式檔案app.py。
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models import db,User,Category

@pytest.fixture
def app():
    db_name = os.environ.get('TEST_DB_NAME', 'Ecommerce_test') 
    db_uri = f'postgresql://postgres:talen168168@localhost:5432/{db_name}'

    app = create_app({
        'SQLALCHEMY_DATABASE_URI': db_uri,
        'TESTING': True,
        'JWT_SECRET_KEY': 'testkey',
    })
    with app.app_context():
        #根據models.py建立db
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
