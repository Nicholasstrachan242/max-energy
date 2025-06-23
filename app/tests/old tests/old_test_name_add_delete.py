# Test adding and deleting rows using Names model with local test database.
# Table is test > testing_1
# Test 1: Add 1 row to table, return the row.
# Test 2: Delete the row that was added in Test 1. Confirm that it is deleted.

import pytest
from app import db
from app.models.Names import Names

# Test 1: Add 1 row to table, return the row.
def test_create_one(app):
    with app.app_context():
        # Clear existing data
        db.session.query(Names).delete()
        db.session.commit()
        
        name = Names(firstname='Temporary', lastname='User')
        db.session.add(name)
        db.session.commit()

        result = db.session.query(Names).filter_by(firstname='Temporary', lastname='User').first()

        # assert
        assert result is not None
        assert result.firstname == 'Temporary'
        assert result.lastname == 'User'

# Test 2: Create a row, then delete it. Confirm that it is deleted.
def test_delete_one(app):
    with app.app_context():
        # Clear existing data
        db.session.query(Names).delete()
        db.session.commit()
        
        # Create a row
        name = Names(firstname='DeleteThis', lastname='User')
        db.session.add(name)
        db.session.commit()
        
        # Check if row exists and delete it
        existing_row = db.session.query(Names).filter_by(firstname='DeleteThis', lastname='User').first()
        assert existing_row is not None, "Row was not created properly"
        
        db.session.delete(existing_row)
        db.session.commit()
        
        # Confirm that the row was deleted
        deleted_row = db.session.query(Names).filter_by(firstname='DeleteThis', lastname='User').first()
        assert deleted_row is None, "Row was not properly deleted"

