import pytest
import sys
import os
#最優先去指定的資料(專案根目錄下) 來imprt程式檔案app.py。
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models import db,User,Category
from unittest.mock import patch

def dummy_append_order_to_sheet(*a, **k):
    return None
# 在不同執行路徑下自動判斷 patch 路徑
PATCH_PATHS = [
    "backend.utils.google_sheets_util.append_order_to_sheet",  # CI/CD 大多這個
    "utils.google_sheets_util.append_order_to_sheet",          # 本地
    "google_sheets_util.append_order_to_sheet",                # 萬一你有直接 import
]

if "pytest" in sys.modules:
    for path in PATCH_PATHS:
        try:
            patch(path, dummy_append_order_to_sheet).start()
        except Exception:
            pass

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
