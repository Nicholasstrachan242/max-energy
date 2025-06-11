# Test the select functionality of the Names model with local test database.
# Table is test > testing_1
# Test 1: select 2 rows manually by name, return only the first in ascending order by id.
# Test 2: select 50 rows, return selected rows in alphabetical order by lastname.


import pytest
import os
from dotenv import load_dotenv
from flask import Flask
from app import db
from app.models.Names import Names

# load environment variables
load_dotenv()

@pytest.fixture
def app():
    app=Flask(__name__)
    db_uri = (
        f"mysql+pymysql://{os.getenv('TEST_DB_USER')}:{os.getenv('TEST_DB_PASS')}"
        f"@{os.getenv('TEST_DB_HOST')}:{os.getenv('TEST_DB_PORT')}/{os.getenv('TEST_DB_NAME')}"
    )

    # show uri
    print(f"\nAttempting to connect with: {db_uri}")

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

# Create session for each test. Flask-SQLAlchemy automatically sets up engine and scoped session.
@pytest.fixture(autouse=True)
def session(app):
    with app.app_context():
        # Start a transaction
        db.session.begin()
        
        yield db.session
        
        db.session.rollback()
        db.session.remove()

# TEST 1: pass in 2 rows manually, return only the first row in ascending order by id.
def test_select_first(session):
    name1 = Names(firstname='John', lastname='Doe')
    name2 = Names(firstname='Big', lastname='Chungus')
    session.add_all([name1, name2])
    session.commit()

    result = session.query(Names).order_by(Names.id.asc()).first()

    # assert
    assert result is not None
    assert result.firstname == 'John'
    assert result.lastname == 'Doe'

    print(f"Row retrieved was: {result}")

# TEST 2: select 50 rows, return selected rows in alphabetical order by lastname.
def test_select_50_rows(session):
    result = session.query(Names).order_by(Names.lastname.asc()).limit(50).all()

    lastnames = [row.lastname for row in result]

    assert len(result) == 50
    assert lastnames == sorted(lastnames)

    print(f"Rows retrieved were: {lastnames}")



