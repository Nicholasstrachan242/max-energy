# Test the select functionality of the Names model with local test database.
# Table is test > testing_1
# Test 1: select 2 rows manually by name, return only the first in ascending order by id.
# Test 2: select 50 rows, return selected rows in alphabetical order by lastname.


import pytest
from app import create_app, db
from app.models.Names import Names

@pytest.fixture
def app():
    app = create_app({
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
        print("DB connection established")
        
        yield db.session
        
        # Rollback the transaction to clean up
        db.session.rollback()
        db.session.remove()

# TEST 1: pass in 2 rows manually, return only the first row in ascending order by id.
def test_select_first(session):
    # clear existing data
    session.query(Names).delete()
    session.commit()
    
    # create test data
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
    # clear existing data
    session.query(Names).delete()
    session.commit()
    
    # create test data
    test_names = [Names(firstname=f'FirstName{i}', lastname=f'LastName{i}') for i in range(50)]
    session.add_all(test_names)
    session.commit()

    result = session.query(Names).order_by(Names.lastname.asc()).limit(50).all()

    lastnames = [row.lastname for row in result]

    assert len(result) == 50
    assert lastnames == sorted(lastnames)

    print(f"Rows retrieved were: {lastnames}")



