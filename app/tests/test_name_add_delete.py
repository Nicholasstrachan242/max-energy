# Test adding and deleting rows using Names model with local test database.
# Table is test > testing_1
# Test 1: Add 1 row to table, return the row.
# Test 2: Delete the row that was added in Test 1. Confirm that it is deleted.

import pytest
from app import create_app, db
from app.models.Names import Names

@pytest.fixture
def app():
    app=create_app({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False
    })
    with app.app_context():
        yield app
        db.session.remove()

# Create session for each test. Flask-SQLAlchemy automatically sets up engine and scoped session.
@pytest.fixture
def session(app):
    with app.app_context():
        # Start a transaction
        db.session.begin()
        
        yield db.session
        
        # rollback the transaction to clean up
        db.session.rollback()
        db.session.remove()

#Test 1: Add 1 row to table, return the row.
def test_create_one(session):
    # Clear existing data
    session.query(Names).delete()
    session.commit()
    
    name = Names(firstname='Temporary', lastname='User')
    session.add(name)
    session.commit()

    result = session.query(Names).filter_by(firstname='Temporary', lastname='User').first()

    # assert
    assert result is not None
    assert result.firstname == 'Temporary'
    assert result.lastname == 'User'

#Test 2: Create a row, then delete it. Confirm that it is deleted.
def test_delete_one(session):
    # Clear existing data
    session.query(Names).delete()
    session.commit()
    
    # Create a row
    name = Names(firstname='DeleteThis', lastname='User')
    session.add(name)
    session.commit()
    
    # Check if row exists and delete it
    existing_row = session.query(Names).filter_by(firstname='DeleteThis', lastname='User').first()
    assert existing_row is not None, "Row was not created properly"
    
    session.delete(existing_row)
    session.commit()
    
    # Confirm that the row was deleted
    deleted_row = session.query(Names).filter_by(firstname='DeleteThis', lastname='User').first()
    assert deleted_row is None, "Row was not properly deleted"

