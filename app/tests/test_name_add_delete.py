# Test adding and deleting rows using Names model with local test database.
# Table is test > testing_1
# Test 1: Add 1 row to table, return the row.
# Test 2: Delete the row that was added in Test 1. Confirm that it is deleted.

import pytest
import os
from dotenv import load_dotenv
from flask import Flask
from app import create_app, db
from app.models.Names import Names

@pytest.fixture
def app():
    app=create_app({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

# Create session for each test. Flask-SQLAlchemy automatically sets up engine and scoped session.
@pytest.fixture(autouse=True)
def session(app):
    with app.app_context():
        # Start a transaction
        db.session.begin()
        
        yield db.session
        
        db.session.rollback()
        db.session.remove()

#Test 1: Add 1 row to table, return the row. Make sure it doesn't already exist.
def test_create_one(session):
    # check if row already exists
    existing_row = session.query(Names).filter_by(firstname='Temporary', lastname='User').first()
    if existing_row:
        pytest.fail("User already exists. Delete the row and try again.")
    else:
        name = Names(firstname='Temporary', lastname='User')
        session.add(name)
        session.commit()

    result = session.query(Names).filter_by(firstname='Temporary', lastname='User').first()

    # assert
    assert result is not None
    assert result.firstname == 'Temporary'
    assert result.lastname == 'User'
    print(f"User added to table: {result}")

#Test 2: Delete the row that was added in Test 1. Confirm that it is deleted.
def test_delete_one(session):
    # check if row exists
    existing_row = session.query(Names).filter_by(firstname='Temporary', lastname='User').first()
    
    if existing_row:
        print(f"Existing row found: {existing_row}. Now Deleting...")
        session.delete(existing_row)
        session.commit()
    else:
        pytest.fail("User does not exist. Add the row and try again.")

